import rapidjson
from flask import jsonify, render_template, request
from flask_restful import Api, Resource, reqparse
from . import devices
from zigbeeLauncher.database.interface import DBDevice, DBZigbee, DBZigbeeEndpoint, DBZigbeeEndpointCluster, \
    DBZigbeeEndpointClusterAttribute
from zigbeeLauncher.mqtt.WiserZigbeeLauncher import dongle_command_2
from zigbeeLauncher.logging import flaskLogger as logger
from ..response import pack_response
from jsonschema import validate, draft7_format_checker
from jsonschema.exceptions import SchemaError, ValidationError

from ..util import check_zigbee_exist, check_device_state, check_device_exist
from ...zigbee.DataType import get_bytes, data_type_value_table, data_type_table


class ZigbeesResource(Resource):
    def get(self):
        """
        获取数据库zigbee表并传给前端
        :return: zigbee所有数据
        """
        if request.args:
            try:
                paras = {}
                for key in request.args:
                    paras[key] = request.args[key]
                data = DBZigbee(**paras).retrieve()
                return pack_response({'code': 0, 'response': data})
            except Exception as e:
                logger.exception("request error")
                return pack_response({'code': 90000}, status=500, error="bad parameters:" + str(request.args))
        else:
            data = DBZigbee().retrieve()
            return pack_response({'code': 0, 'response': data})
        # return render_template('show_all_devices.html', devices=Device.query.all())


class ZigbeeResource(Resource):
    commands = ['join', 'leave', 'attribute', 'data_request']
    schema = {
        "type": "object",
        "properties": {
            "join": {
                "type": "object",
                "properties": {
                    "channel_mask": {
                        "type": "integer",
                        "description": "network channel mask, 4 bytes, all channel: 0x7FFF800, channel 11: 0x800, channel 12: 0x1000..."
                    },
                    "auto_option": {
                        "type": "integer",
                        "description": "auto option setting, this property value should be 0, 1, 2, 3"
                    },
                    "pan_id": {
                        "type": "integer",
                        "description": "network PAN ID, 2 bytes, set this property if 'auto_option' is 0 or 2,"
                    },
                    "extended_pan_id": {
                        "type": "integer",
                        "description": "network extended PAN ID, 8 bytes, set this property if 'auto_option' is 0 or 1"
                    }
                },
                "required": [
                    "channel_mask",
                    "auto_option"
                ],
                "description": "join command, trigger device joining to a specific zigbee network\n"
            },
            "leave": {
                "type": "object",
                "properties": {},
                "description": "leave command, trigger device leaving to current zigbee network"
            },
            "data_request": {
                "type": "object",
                "properties": {},
                "description": "data request command, trigger sleepy end device send out data_request_command\n"
            },
            "attribute": {
                "type": "object",
                "properties": {
                    "endpoint": {
                        "type": "integer",
                        "description": "endpoint id, rang 1-240"
                    },
                    "cluster": {
                        "type": "integer",
                        "description": "cluster ID, range 0-65535"
                    },
                    "server": {
                        "type": "boolean",
                        "description": "server cluster mask"
                    },
                    "manufacturer": {
                        "type": "boolean",
                        "description": "manufacturer specific mask fro this cluster"
                    },
                    "manufacturer_code": {
                        "type": "integer",
                        "description": "manufacturer code for this cluster if manufacturer is true, range 0-65535"
                    },
                    "attribute": {
                        "type": "integer",
                        "description": "attribute ID, range 0-65535"
                    },
                    "type": {
                        "type": "string",
                        "description": "attribute type, provide this property when attribute_manufacturer is true"
                    },
                    "value": {
                        "oneOf": [
                            {
                                "type": "integer",
                                "description": "integer data"
                            },
                            {
                                "type": "string",
                                "description": "string data"
                            }
                        ],
                        "description": "attribute value, could be integer or string"
                    }
                },
                "required": [
                    "endpoint",
                    "cluster",
                    "server",
                    "attribute",
                    "manufacturer",
                    "value",
                    "type"
                ]
            }
        }
    }

    @check_zigbee_exist
    def get(self, mac, zigbee):
        return pack_response({'code': 0, 'response': zigbee})

    @check_device_state
    def put(self, mac, device):
        args = request.get_json()
        ip = device['ip']
        try:
            for key in args.keys():
                if key not in self.commands:
                    return pack_response({'code': 90002}, status=500, command=key)
            for key in args.keys():
                command = key
                payload = args[key]
                try:
                    validate(instance=args, schema=self.schema,
                             format_checker=draft7_format_checker)
                    if command == 'join':
                        # 验证channel和auto_option的合法性
                        channel = payload['channel_mask']
                        auto_option = payload['auto_option']
                        if not auto_option & 0x1 and 'pan_id' not in payload:
                            return pack_response({'code': 90001}, status=500, item='pan_id')
                        if not auto_option & 0x2 and 'extended_pan_id' not in payload:
                            return pack_response({'code': 90001}, status=500, item='extended_pan_id')
                        # 校验数据大小
                        if channel < 0x800 or channel > 0x7FFF800:
                            return pack_response({'code': 90005}, status=500, value='channel_mask')
                        if auto_option > 3 or auto_option < 0:
                            return pack_response({'code': 90005}, status=500, value='auto_option')
                        if 'pan_id' in payload:
                            pan_id = payload['pan_id']
                            if pan_id < 0 or pan_id > 0xFFFF:
                                return pack_response({'code': 90005}, status=500, value='channel_mask')
                        if 'extended_pan_id' in payload:
                            extended_pan_id = payload['extended_pan_id']
                            if extended_pan_id < 0 or extended_pan_id > 0xFFFFFFFFFFFFFFFF:
                                return pack_response({'code': 90005}, status=500, value='channel_mask')
                        # 验证设备是否已经入网
                        zigbee = DBZigbee(mac=mac).retrieve()
                        if not zigbee:
                            return pack_response({'code': 10000}, status=404, device=mac)
                        if zigbee[0]['pan_id'] != "FFFF":
                            return pack_response({'code': 40001}, status=500, device=mac)
                    elif command == 'leave':
                        # 验证设备是否已经入网
                        zigbee = DBZigbee(mac=mac).retrieve()
                        if not zigbee:
                            return pack_response({'code': 10000}, status=404, device=mac)
                        if zigbee[0]['pan_id'] == "FFFF":
                            return pack_response({'code': 40000}, status=500, device=mac)
                    elif command == 'attribute':
                        # 验证manufacturer
                        manufacturer = payload['manufacturer']
                        if manufacturer and 'manufacturer_code' not in payload:
                            return pack_response({'code': 90001}, status=500, item='manufacturer_code')
                        # 验证type是否可以找到
                        type = payload['type']
                        if type not in data_type_value_table:
                            return pack_response({'code': 30001}, status=500, type=type)
                        else:
                            type = data_type_value_table[type]
                        # 验证整型数据合法性
                        len = data_type_table[type]
                        value = payload['value']
                        if isinstance(value, int):
                            if len == 0:
                                # 数据类型错误
                                return pack_response({'code': 30002}, status=500)
                            else:
                                # 验证整型数据是否超出范围
                                if 0x28 <= type <= 0x2f:
                                    maximum = (1 << 8 * len) / 2
                                    if not (-maximum) <= value < maximum:
                                        return pack_response({'code': 90005}, status=500, value='value')
                                    # 将负数转换
                                    value_wrap = abs(~abs(value)) + 1
                                    payload['value'] = value_wrap
                                else:
                                    if not 0 <= value <= (1<<8*len):
                                        return pack_response({'code': 90005}, status=500, value='value')
                        else:
                            if len != 0:
                                # 数据类型错误
                                return pack_response({'code': 30002}, status=500)
                        # 验证整型数据范围
                        endpoint = payload['endpoint']
                        if not 0 < endpoint <= 240:
                            return pack_response({'code': 90005}, status=500, value='endpoint')
                        cluster = payload['cluster']
                        if not 0 <= cluster <= 0xFFFF:
                            return pack_response({'code': 90005}, status=500, value='cluster')
                        attribute = payload['attribute']
                        if not 0 <= attribute <= 0xFFFF:
                            return pack_response({'code': 90005}, status=500, value='attribute')
                        if 'manufacturer_code' in payload:
                            code = payload['manufacturer_code']
                            if not 0 <= code <= 0xFFFF:
                                return pack_response({'code': 90005}, status=500, value='manufacturer_code')
                    elif command == 'data_request':
                        pass
                except SchemaError as e:
                    logger.exception('illegal schema: %s', e.message)
                    return pack_response({'code': 90003}, status=500, error=e.message)
                except ValidationError as e:
                    logger.exception('json validation failed:%s', e.message)
                    return pack_response({'code': 90004}, status=500, error=e.message)
                else:
                    response = dongle_command_2(ip, mac, args)
                    code = response['code']
                    if code != 0:
                        return pack_response(response, status=500)
                    else:
                        return pack_response(response)
        except Exception as e:
            logger.exception("request error:")
            return pack_response({'code': 90000}, status=500, error=str(e))


class ZigbeeAttributesResource(Resource):
    @check_device_exist
    def get(self, mac, device):
        """
        通过endpoint, cluster, attribute获取属性列表
        :param mac:
        :param device:
        :return:
        """
        ip = device['ip']
        paras = {}
        if request.args:
            try:
                for key in request.args:
                    paras[key] = int(request.args[key])
                paras['mac'] = mac
                if 'endpoint' not in paras:
                    return pack_response({'code': 90001}, status=500, item='endpoint')
                if 'cluster' not in paras:
                    return pack_response({'code': 90001}, status=500, item='cluster')
                if 'server' not in paras:
                    return pack_response({'code': 90001}, status=500, item='server')
                if 'manufacturer' not in paras:
                    return pack_response({'code': 90001}, status=500, item='manufacturer')
                else:
                    if bool(paras['manufacturer']) and 'manufacturer_code' not in paras:
                        return pack_response({'code': 90001}, status=500, item='manufacturer_code')
                if 'attribute' not in paras:
                    return pack_response({'code': 90001}, status=500, item='attribute')
            except Exception as e:
                logger.exception("request error")
                return pack_response({'code': 90000}, status=500, error="bad parameters:" + str(request.args))
            response = dongle_command_2(ip, mac, {'attribute': paras})
            code = response['code']
            if code != 0:
                return pack_response(response, status=500)
            else:
                return pack_response(response)
        else:
            return pack_response({'code': 90001}, status=500, item='endpoint')

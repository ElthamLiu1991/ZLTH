import rapidjson
from flask import jsonify, render_template, request
from flask_restful import Api, Resource, reqparse
from . import devices
from zigbeeLauncher.database.interface import DBDevice, DBZigbee
from zigbeeLauncher.mqtt.Launcher_API import dongle_command_2
from zigbeeLauncher.logging import flaskLogger as logger
from ..response import Response
from jsonschema import validate, draft7_format_checker
from jsonschema.exceptions import SchemaError, ValidationError

from ..util import check_zigbee_exist, check_device_state, check_device_exist
from ...zigbee import type_exist, format_validation, value_validation
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
                for item in data:
                    item['extended_pan_id'] = int(item['extended_pan_id'], 16)
                return Response(data=data).pack()
            except Exception as e:
                logger.exception("request error")
                return Response("bad parameters:" + str(request.args), code=90000).pack()
        else:
            data = DBZigbee().retrieve()
            for item in data:
                item['extended_pan_id'] = int(item['extended_pan_id'], 16)
            return Response(data=data).pack()
        # return render_template('show_all_devices.html', devices=Device.query.all())


class ZigbeeResource(Resource):
    commands = ['join', 'leave', 'attribute', 'data_request']
    schema = {
                "type": "object",
                "properties": {
                  "join": {
                    "type": "object",
                    "properties": {
                      "channels": {
                        "description": "network channels, 11,12,13, ..., 26",
                        "type": "array",
                        "items": {
                          "type": "integer"
                        }
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
                      "channels"
                    ],
                    "description": "join command, trigger device joining to a specific zigbee network\n",
                    "x-apifox-orders": [
                      "channels",
                      "pan_id",
                      "extended_pan_id"
                    ],
                    "x-apifox-ignore-properties": []
                  },
                  "leave": {
                    "type": "object",
                    "properties": {},
                    "description": "leave command, trigger device leaving to current zigbee network",
                    "x-apifox-orders": [],
                    "x-apifox-ignore-properties": []
                  },
                  "data_request": {
                    "type": "object",
                    "properties": {},
                    "description": "data request command, trigger sleepy end device send out data_request_command\n",
                    "x-apifox-orders": [],
                    "x-apifox-ignore-properties": []
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
                        "description": "manufacturer code for this cluster if cluster_manufacturer is true, range 0-65535"
                      },
                      "attribute": {
                        "type": "integer",
                        "description": "attribute ID, range 0-65535"
                      },
                      "type": {
                        "type": "string",
                        "description": "attribute type"
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
                      "manufacturer",
                      "attribute",
                      "type",
                      "value"
                    ],
                    "description": "change attribute value",
                    "x-apifox-orders": [
                      "endpoint",
                      "cluster",
                      "server",
                      "manufacturer",
                      "manufacturer_code",
                      "attribute",
                      "type",
                      "value"
                    ],
                    "x-apifox-ignore-properties": []
                  }
                },
                "x-apifox-orders": [
                  "join",
                  "leave",
                  "data_request",
                  "attribute"
                ],
                "x-apifox-ignore-properties": []
              }

    @check_zigbee_exist
    def get(self, mac, zigbee):
        zigbee['extended_pan_id'] = int(zigbee['extended_pan_id'], 16)
        return Response(data=zigbee).pack()

    @check_device_state
    def put(self, mac, device):
        args = request.get_json()
        ip = device['ip']
        try:
            for key in args.keys():
                if key not in self.commands:
                    return Response(key, code=90002).pack()
            for key in args.keys():
                command = key
                payload = args[key]
                try:
                    validate(instance=args, schema=self.schema,
                             format_checker=draft7_format_checker)
                    if command == 'join':
                        # 验证channel和auto_option的合法性
                        channel = payload['channels']
                        channel_all = list(range(11, 27))
                        if not set(channel) <= set(channel_all):
                            return Response(channel, code=90005).pack()
                        if 'pan_id' in payload:
                            pan_id = payload['pan_id']
                            if pan_id < 0 or pan_id > 0xFFFF:
                                return Response('pan_id', code=90005).pack()
                        if 'extended_pan_id' in payload:
                            extended_pan_id = payload['extended_pan_id']
                            if extended_pan_id < 0 or extended_pan_id > 0xFFFFFFFFFFFFFFFF:
                                return Response('extended_pan_id', code=90005).pack()
                        # 验证设备是否已经入网
                        zigbee = DBZigbee(mac=mac).retrieve()
                        if not zigbee:
                            return Response(mac, code=10000).pack()
                        if zigbee[0]['pan_id'] != 0xFFFF:
                            return Response(mac, code=40001).pack()
                    elif command == 'leave':
                        # 验证设备是否已经入网
                        zigbee = DBZigbee(mac=mac).retrieve()
                        if not zigbee:
                            return Response(mac, code=10000).pack()
                        if zigbee[0]['pan_id'] == 0xFFFF:
                            return Response(mac, code=40000).pack()
                    elif command == 'attribute':
                        # 验证manufacturer
                        manufacturer = payload['manufacturer']
                        if manufacturer and 'manufacturer_code' not in payload:
                            return Response('manufacturer_code', code=90001).pack()
                        # 验证type是否可以找到
                        type = payload['type']
                        value = payload['value']
                        if isinstance(value, str):
                            if 'length' not in payload:
                                return Response('length', code=90001).pack()
                            if len(value) > payload['length']:
                                return Response(value, code=90005).pack()
                        if not type_exist(type):
                            return Response(type, code=30001).pack()
                        if not format_validation(type, value):
                            return Response(code=30002).pack()
                        if not value_validation(type, value):
                            return Response(value, code=90005).pack()
                        # 验证整型数据范围
                        endpoint = payload['endpoint']
                        if not 0 < endpoint <= 240:
                            return Response('endpoint', code=90005).pack()
                        cluster = payload['cluster']
                        if not 0 <= cluster <= 0xFFFF:
                            return Response('cluster', code=90005).pack()
                        attribute = payload['attribute']
                        if not 0 <= attribute <= 0xFFFF:
                            return Response('attribute', code=90005).pack()
                        if 'manufacturer_code' in payload:
                            code = payload['manufacturer_code']
                            if not 0 <= code <= 0xFFFF:
                                return Response('manufacturer_code', code=90005).pack()
                    elif command == 'data_request':
                        pass
                except SchemaError as e:
                    logger.exception('illegal schema: %s', e.message)
                    return Response(e.message, code=90003).pack()
                except ValidationError as e:
                    logger.exception('json validation failed:%s', e.message)
                    return Response(e.message, code=90004).pack()
                else:
                    response = dongle_command_2(ip, mac, args)
                    return Response(**response).pack()
        except Exception as e:
            logger.exception("request error:")
            return Response(str(e), code=90000).pack()


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
                    return Response('endpoint', code=90001).pack()
                if 'cluster' not in paras:
                    return Response('cluster', code=90001).pack()
                if 'server' not in paras:
                    return Response('server', code=90001).pack()
                if 'manufacturer' not in paras:
                    return Response('manufacturer', code=90001).pack()
                else:
                    if bool(paras['manufacturer']) and 'manufacturer_code' not in paras:
                        return Response('manufacturer_code', code=90001).pack()
                if 'attribute' not in paras:
                    return Response('attribute', code=90001).pack()
            except Exception as e:
                logger.exception("request error")
                return Response("bad parameters:" + str(request.args), code=90000).pack()
            response = dongle_command_2(ip, mac, {'attribute': paras})
            return Response(**response).pack()
        else:
            return Response('endpoint', code=90001).pack()

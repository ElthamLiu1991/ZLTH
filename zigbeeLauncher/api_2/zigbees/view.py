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


def get_endpoints(mac):
    result = []
    endpoints = DBZigbeeEndpoint(mac=mac).retrieve()
    if endpoints:
        for endpoint in endpoints:
            del endpoint['id']
            del endpoint['mac']
            endpoint_id = endpoint['endpoint']
            server_clusters = []
            client_clusters = []
            clusters = DBZigbeeEndpointCluster(mac=mac, endpoint=endpoint_id).retrieve()
            if clusters:
                for cluster in clusters:
                    if cluster['server']:
                        tmp = []
                        attributes = DBZigbeeEndpointClusterAttribute(
                            mac=mac, endpoint=endpoint_id, server=True, cluster=cluster['cluster']).retrieve()
                        if attributes:
                            for attribute in attributes:
                                tmp.append({
                                    'attribute': attribute['attribute'],
                                    'name': attribute['name'],
                                    "type": attribute['type'],
                                    "value": attribute['value']
                                })
                        server_clusters.append({
                            'cluster': cluster['cluster'],
                            'name': cluster['name'],
                            'manufacturer': cluster['manufacturer'],
                            'manufacturer_code': cluster['manufacturer_code'],
                            'attributes': tmp
                        })
                    else:
                        tmp = []
                        attributes = DBZigbeeEndpointClusterAttribute(
                            mac=mac, endpoint=endpoint_id, server=False, cluster=cluster['cluster']).retrieve()
                        if attributes:
                            for attribute in attributes:
                                tmp.append({
                                    'attribute': attribute['attribute'],
                                    'name': attribute['name'],
                                    "type": attribute['type'],
                                    "value": attribute['value']
                                })
                        client_clusters.append({
                            'cluster': cluster['cluster'],
                            'name': cluster['name'],
                            'manufacturer': cluster['manufacturer'],
                            'manufacturer_code': cluster['manufacturer_code'],
                            'attributes': tmp
                        })
            endpoint['server_clusters'] = server_clusters
            endpoint['client_clusters'] = client_clusters
            result.append(endpoint)
    return result


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
                if data:
                    for zigbee in data:
                        zigbee['endpoints'] = get_endpoints(zigbee['mac'])
                return pack_response(0, data)
            except Exception as e:
                logger.exception("request error")
                return pack_response(90000, error="bad parameters:" + str(request.args)), 500
        else:
            data = DBZigbee().retrieve()
            if data:
                for zigbee in data:
                    zigbee['endpoints'] = get_endpoints(zigbee['mac'])
            return pack_response(0, data)
        # return render_template('show_all_devices.html', devices=Device.query.all())


join_schema = {
                "type": "object",
                "properties": {
                  "join": {
                    "type": "object",
                    "properties": {
                      "channel_mask": {
                        "type": "string",
                        "description": "network channel mask, all channel: 7FFF800"
                      },
                      "auto_option": {
                        "type": "integer",
                        "description": "auto option setting, this property value should be 0, 1, 2, 3"
                      },
                      "pan_id": {
                        "type": "string",
                        "description": "network PAN ID, set this property if 'auto_option' is 0 or 2"
                      },
                      "extended_pan_id": {
                        "type": "string",
                        "description": "network extended PAN ID, set this property if 'auto_option' is 0 or 1"
                      }
                    },
                    "required": [
                      "channel_mask",
                      "auto_option",
                      "pan_id",
                      "extended_pan_id"
                    ],
                    "description": "join command"
                  }
                },
                "required": [
                  "join"
                ]
              }

leave_schema = {
            "type": "object",
            "properties": {
              "leave": {
                "type": "object",
                "properties": {},
                "description": "leave command"
              }
            },
            "required": [
              "leave"
            ]
          }

attribute_schema = {
            "type": "object",
            "properties": {
              "attribute": {
                "type": "object",
                "properties": {
                  "endpoint": {
                    "type": "integer",
                    "description": "endpoint ID"
                  },
                  "cluster": {
                    "type": "string",
                    "description": "cluster ID"
                  },
                  "server": {
                    "type": "boolean",
                    "description": "server or client "
                  },
                  "attribute": {
                    "type": "string",
                    "description": "attribute ID"
                  },
                  "value": {
                    "type": "string",
                    "description": "attribute value"
                  }
                },
                "required": [
                  "endpoint",
                  "cluster",
                  "server",
                  "attribute",
                  "value"
                ],
                "description": "attribute command"
              }
            },
            "required": [
              "attribute"
            ]
          }

data_request_schema = {
            "type": "object",
            "properties": {
              "data_request": {
                "type": "object",
                "properties": {},
                "description": "data request command"
              }
            },
            "required": [
              "data_request"
            ]
          }


class ZigbeeResource(Resource):

    commands = ['join', 'leave', 'attribute', 'data_request']

    def get(self, mac):
        zigbee = DBZigbee(mac=mac).retrieve()
        if zigbee:
            zigbee = zigbee[0]
            zigbee['endpoints'] = get_endpoints(zigbee['mac'])
            return pack_response(0, zigbee), 200
        else:
            return pack_response(10000, device=mac), 404

    def put(self, mac):
        args = request.get_json()
        device = DBDevice(mac=mac).retrieve()
        if device:
            try:
                connected = device[0]['connected']
                ip = device[0]['ip']
                if connected:
                    for key in args.keys():
                        if key not in self.commands:
                            return pack_response(90002, command=key), 500
                    for key in args.keys():
                        command = key
                        try:
                            validate(instance=args, schema=eval(key+'_schema'),
                                     format_checker=draft7_format_checker)
                            if command == 'join':
                                # 验证channel和auto_option的合法性
                                channel = int(args[key]['channel_mask'], 16)
                                if channel < 0x800 or channel > 0x7FFF800:
                                    return pack_response(90005, item='channel_mask'), 500
                                auto_option = args[key]['auto_option']
                                if auto_option > 3:
                                    return pack_response(90005, item='auto_option'), 500
                                # 验证设备是否已经入网
                                zigbee = DBZigbee(mac=mac).retrieve()
                                if not zigbee:
                                    return pack_response(10000, device=mac), 404
                                if zigbee[0]['pan_id'] != "FFFF":
                                    return pack_response(40001, device=mac), 500
                            elif command == 'leave':
                                # 验证设备是否已经入网
                                zigbee = DBZigbee(mac=mac).retrieve()
                                if not zigbee:
                                    return pack_response(10000, device=mac), 404
                                if zigbee[0]['pan_id'] == "FFFF":
                                    return pack_response(40000, device=mac), 500
                            elif command == 'attribute':
                                payload = args[key]
                                # 判断attribute是否存在
                                attribute = DBZigbeeEndpointClusterAttribute(
                                    mac=mac,
                                    endpoint=payload['endpoint'],
                                    cluster=payload['cluster'],
                                    server=payload['server'],
                                    attribute=payload['attribute']
                                ).retrieve()
                                if not attribute:
                                    return pack_response(30000, attribute=payload['attribute']), 500
                                else:
                                    # 获取manufacturer_code
                                    cluster = DBZigbeeEndpointCluster(
                                        mac=mac,
                                        endpoint=payload['endpoint'],
                                        cluster=payload['cluster'],
                                        server=payload['server']
                                    ).retrieve()
                                    if not cluster:
                                        return pack_response(30000, attribute=payload['attribute']), 500
                                    payload['manufacturer_code'] = cluster[0]['manufacturer_code']
                                    payload['type'] = attribute[0]['type']
                            elif command == 'data_request':
                                pass
                        except SchemaError as e:
                            logger.exception('illegal schema: %s', e.message)
                            return pack_response(90003, error=e.message)
                        except ValidationError as e:
                            logger.exception('json validation failed:%s', e.message)
                            return pack_response(90004, error=e.message)
                        else:
                            dongle_command_2(ip, mac, args)
                            return pack_response(0)
                else:
                    return pack_response(10001, device=mac), 500
            except Exception as e:
                logger.exception("request error:")
                return pack_response(90000, error=str(e)), 500
        else:
            return pack_response(10000, device=mac), 404

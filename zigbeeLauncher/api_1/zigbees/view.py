import rapidjson
from flask import jsonify, render_template, request
from flask_restful import Api, Resource, reqparse
from . import devices
from zigbeeLauncher.database.interface import DBDevice, DBZigbee, DBZigbeeEndpoint, DBZigbeeEndpointCluster, \
    DBZigbeeEndpointClusterAttribute
from zigbeeLauncher.mqtt.WiserZigbeeLauncher import dongle_command
from zigbeeLauncher.logging import flaskLogger as logger
from ..response import pack_response


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
                                    "type": attribute['type'],
                                    "value": attribute['value']
                                })
                        server_clusters.append({
                            'cluster': cluster['cluster'],
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
                                    "type": attribute['type'],
                                    "value": attribute['value']
                                })
                        client_clusters.append({
                            'cluster': cluster['cluster'],
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
                return pack_response(90000, error="bad parameters:"+str(request.args)), 500
        else:
            data = DBZigbee().retrieve()
            if data:
                for zigbee in data:
                    zigbee['endpoints'] = get_endpoints(zigbee['mac'])
            return pack_response(0, data)
        # return render_template('show_all_devices.html', devices=Device.query.all())


class ZigbeeResource(Resource):

    def get(self, mac):
        zigbee = DBZigbee(mac=mac).retrieve()
        if zigbee:
            zigbee = zigbee[0]
            zigbee['endpoints'] = get_endpoints(zigbee['mac'])
            return pack_response(0, zigbee), 200
        else:
            return pack_response(10000, device=mac), 404

    def put(self, mac):
        parser = reqparse.RequestParser()
        parser.add_argument("command", type=str, required=True, help="please provide command")
        parser.add_argument("payload", type=dict, required=False)
        args = parser.parse_args()
        device = DBDevice(mac=mac).retrieve()
        if device:
            try:
                if device[0]['connected']:
                    command = args['command']
                    if command == 'join':
                        """
                        1. 验证payload是否提供完全
                        2. 验证设备是否已经加入网络
                        """
                        if 'payload' not in args:
                            return pack_response(90001), 500
                        payload = args['payload']
                        validator = rapidjson.Validator('{"required":["channel_mask", "auto_option"]}')
                        validator(rapidjson.dumps(payload))
                        option = payload['auto_option']
                        if option == 0 and 'pan_id' in payload and 'extended_pan_id' in payload:
                            pass
                        elif option == 1 and 'extended_pan_id' in payload:
                            payload['pan_id'] = "0000"
                        elif option == 2 and 'pan_id' in payload:
                            payload['extended_pan_id'] = "0000000000000000"
                        elif option == 3:
                            payload['pan_id'] = "0000"
                            payload['extended_pan_id'] = "0000000000000000"
                        else:
                            return pack_response(90001), 500
                        zigbee = DBZigbee(mac=mac).retrieve()
                        if not zigbee:
                            return pack_response(10000, device=mac), 404
                        if zigbee[0]['pan_id'] != "FFFF":
                            return pack_response(40001, device=mac), 500
                    elif command == 'leave':
                        """
                        1. 判断设备是否在网络中
                        """
                        zigbee = DBZigbee(mac=mac).retrieve()
                        if not zigbee:
                            return pack_response(10000, device=mac), 404
                        if zigbee[0]['pan_id'] == "FFFF":
                            return pack_response(40000, device=mac), 500
                    elif command == 'attribute':
                        """
                        1. 验证payload是否提供完全
                        2. 判断attribute是否存在
                        3. 获取manufacturer_code
                        """
                        if 'payload' not in args:
                            return pack_response(90001), 500
                        payload = args['payload']
                        validator = rapidjson.Validator('{"required":["endpoint", "cluster", "server", '
                                                        '"attribute", "value"]}')
                        validator(rapidjson.dumps(payload))
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
                    else:
                        return pack_response(90002, command=command), 500
                    dongle_command(device[0]["ip"], mac, args)
                    return pack_response(0), 200
                else:
                    return pack_response(10001, device=mac), 500
            except rapidjson.ValidationError as e:
                return pack_response(90001), 500
            except Exception as e:
                logger.exception("request error:")
                return pack_response(90000, error=str(e)), 500
        else:
            return pack_response(10000, device=mac), 404

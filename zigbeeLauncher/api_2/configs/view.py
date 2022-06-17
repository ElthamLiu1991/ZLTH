# -- coding: utf-8 --
import json
import os

import werkzeug
import yaml
from flask import jsonify, render_template, request
from flask_restful import Api, Resource, reqparse
from werkzeug.utils import secure_filename

from zigbeeLauncher.database.interface import DBDevice, DBZigbee, DBZigbeeEndpoint, DBZigbeeEndpointCluster, \
    DBZigbeeEndpointClusterAttribute
from zigbeeLauncher.mqtt.Launcher_API import dongle_command_2, simulator_command_2
from zigbeeLauncher.logging import flaskLogger as logger
from ..json_schemas import config_schema
from ..response import pack_response
from jsonschema import validate, draft7_format_checker
from jsonschema.exceptions import SchemaError, ValidationError

from ..util import handle_devices, check_device_exist, check_device_state, config_validation
from ... import base_dir
from ...mqtt import get_mac_address, get_ip_address


class ConfigResource(Resource):

    def post(self):
        """
        创建一个配置模板
        :return:
        """
        args = request.get_json()
        try:
            if 'filename' not in args and 'config' not in args:
                return pack_response({'code': 90001}, status=500)
            validate(instance=args, schema=config_schema,
                     format_checker=draft7_format_checker)
            result, error = config_validation(args['config'])
            if not result:
                return pack_response({'code':90005}, status=500, value=error)
            # save to file
            filename = args['filename']
            with open(os.path.join(base_dir, './files') + '/' + filename, 'w+') as f:
                yaml.safe_dump(args['config'], f)
            return pack_response({'code':0})
        except SchemaError as e:
            logger.exception('illegal schema: %s', e.message)
            return pack_response({'code':90003}, status=500, error=e.message)
        except ValidationError as e:
            logger.exception('json validation failed:%s', e.message)
            return pack_response({'code':90004}, status=500, error=e.message)


class ConfigFilesResource(Resource):

    def get(self):
        """
        获o取模板列表, 并显示缩略信息，包含device_type, endpint内容
        """
        data = []
        for root, dirs, files in os.walk(os.path.join(base_dir, './files')):
            for file in files:
                details = {}
                with open(root + '/' + file, 'r') as f:
                    try:
                        y = yaml.safe_load(f.read())
                        details['filename'] = file
                        details['device_type'] = y['node']['device_type']
                        details['endpoints'] = []
                        for endpoint in y['endpoints']:
                            server_clusters = []
                            client_clusters = []
                            for cluster in endpoint['server_clusters']:
                                server_clusters.append(cluster['id'])
                            for cluster in endpoint['client_clusters']:
                                client_clusters.append(cluster['id'])
                            details['endpoints'].append({
                                "id": endpoint['id'],
                                "device_id": endpoint['device_id'],
                                "profile_id": endpoint['profile_id'],
                                "server_clusters": server_clusters,
                                "client_clusters": client_clusters
                            })
                        data.append(details)
                    except Exception as e:
                        logger.exception("load yaml failed")
                        continue
            return pack_response({'code':0, 'response':data})

    def post(self):
        """
        上传一个模板文件
        :return:
        """
        parser = reqparse.RequestParser()
        parser.add_argument('file', type=werkzeug.datastructures.FileStorage, location='files')
        args = parser.parse_args()
        content = args.get('file')
        if not content:
            return pack_response({'code': 50001}, status=500, file=None)
        try:
            y = yaml.safe_load(content.read())
            validate(instance={'config': y}, schema=config_schema,
                     format_checker=draft7_format_checker)
            # 验证文件每个字段的值是否符合要求
            result, error = config_validation(args['config'])
            if not result:
                return pack_response({'code': 90005}, status=500, value=error)
            filename = secure_filename(content.filename)
            content.seek(0)
            content.save(os.path.join('./files', filename))
            return pack_response({'code':0})
        except SchemaError as e:
            logger.exception('illegal schema: %s', e.message)
            return pack_response({'code':90003}, status=500, error=e.message)
        except ValidationError as e:
            logger.exception('json validation failed:%s', e.message)
            return pack_response({'code':90004}, status=500, error=e.message)
        except Exception as e:
            logger.exception('load YAML failed:%s', str(e))
            return pack_response({'code':90000}, status=500, error=str(e))

    def delete(self):
        """
        删除所有模板文件
        :return:
        """
        for root, dirs, files in os.walk(os.path.join(base_dir, './files')):
            for file in files:
                if os.path.isfile(root + '/' + file):
                    os.remove(root + '/' + file)
        return pack_response({'code':0})


class ConfigFileResource(Resource):
    def get(self, file):
        """
        获取模板文件
        """
        data = {}
        try:
            with open(os.path.join(base_dir, './files') + '/' + file, 'r') as f:
                try:
                    y = yaml.safe_load(f.read())
                    data['filename'] = file
                    data['config'] = y
                except Exception as e:
                    logger.exception("load yaml failed")
                    return pack_response({'code':50001}, status=500, file=file)
        except FileNotFoundError:
            return pack_response({'code': 50000}, status=404, file=file)
        return pack_response({'code':0, 'response': data})

    def delete(self, file):
        """
        删除当前模板文件
        :return:
        """
        if os.path.isfile(os.path.join(base_dir, './files') + '/' + file):
            os.remove(os.path.join(base_dir, './files') + '/' + file)
            return pack_response({'code':0})
        else:
            return pack_response({'code':50000}, status=404, file=file)


class ConfigDevicesResource(Resource):
    def put(self):
        """
        批量更新设备配置, 使用文件或直接配置
        """
        args = request.get_json()
        if 'devices' not in args:
            return pack_response({'code': 90001}, status=500, item='devices')
        if 'filename' in args:
            file = args['filename']
            path = os.path.join(base_dir, './files') + '/' + file
            if not os.path.isfile(path):
                return pack_response({'code': 50000}, status=500, file=file)
            else:
                with open(path, 'r') as f:
                    data = yaml.safe_load(f.read())
        elif 'config' in args:
            try:
                validate(instance=args, schema=config_schema,
                         format_checker=draft7_format_checker)
                result, error = config_validation(args['config'])
                if not result:
                    return pack_response({'code': 90005}, status=500, value=error)
                data = args['config']
            except SchemaError as e:
                logger.exception('illegal schema: %s', e.message)
                return pack_response({'code': 90003}, status=500, error=e.message)
            except ValidationError as e:
                logger.exception('json validation failed:%s', e.message)
                return pack_response({'code': 90004}, status=500, error=e.message)
        else:
            return pack_response({'code': 90001}, status=500, item='filename or config')

        result, code = handle_devices(args['devices'])
        if code != 200:
            return result, code
        payload = {}
        payload.update(data)
        for ip in result.keys():
            payload['devices'] = result[ip]
            response = simulator_command_2(ip, {
                'config': payload
            })
            code = response['code']
            if code != 0:
                return pack_response(response, status=500)
        return pack_response(response)
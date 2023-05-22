# -- coding: utf-8 --
import json
import os

import werkzeug
import yaml
from flask import jsonify, render_template, request
from flask_restful import Api, Resource, reqparse
from werkzeug.utils import secure_filename

from zigbeeLauncher.logging import flaskLogger as logger
from ..json_schemas import config_schema
from jsonschema import validate, draft7_format_checker

from ..util import config_validation, send_command
from ... import base_dir
from ...database.interface import DBDevice
from ...exceptions import exception, InvalidPayload, NotFound, DeviceNotFound, DeviceOffline


class ConfigResource(Resource):
    """
    /configs
    """

    def post(self):
        """
        保存一个配置模板
        :return:
        """
        schema = {
            "type": "object",
            "properties": {
                "filename": {
                    "type": "string"
                },
                "config": {
                    "type": "object",
                    "properties": {
                        "endpoints": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "client_clusters": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "attributes": {
                                                    "type": "array",
                                                    "items": {
                                                        "type": "object",
                                                        "properties": {
                                                            "default": {
                                                                "oneOf": [
                                                                    {
                                                                        "type": "string"
                                                                    },
                                                                    {
                                                                        "type": "integer"
                                                                    }
                                                                ]
                                                            },
                                                            "id": {
                                                                "type": "integer"
                                                            },
                                                            "length": {
                                                                "type": "integer"
                                                            },
                                                            "manufacturer": {
                                                                "type": "boolean"
                                                            },
                                                            "manufacturer_code": {
                                                                "type": "integer"
                                                            },
                                                            "name": {
                                                                "type": "string"
                                                            },
                                                            "type": {
                                                                "type": "string"
                                                            },
                                                            "writable": {
                                                                "type": "boolean"
                                                            }
                                                        },
                                                        "required": [
                                                            "default",
                                                            "id",
                                                            "manufacturer",
                                                            "type",
                                                            "writable"
                                                        ],
                                                        "x-apifox-orders": [
                                                            "default",
                                                            "id",
                                                            "length",
                                                            "manufacturer",
                                                            "manufacturer_code",
                                                            "name",
                                                            "type",
                                                            "writable"
                                                        ],
                                                        "x-apifox-ignore-properties": []
                                                    }
                                                },
                                                "commands": {
                                                    "type": "object",
                                                    "properties": {
                                                        "S->C": {
                                                            "type": "array",
                                                            "items": {
                                                                "type": "object",
                                                                "properties": {
                                                                    "description": {
                                                                        "type": "string"
                                                                    },
                                                                    "id": {
                                                                        "type": "integer"
                                                                    },
                                                                    "manufacturer": {
                                                                        "type": "boolean"
                                                                    },
                                                                    "manufacturer_code": {
                                                                        "type": "integer"
                                                                    }
                                                                },
                                                                "required": [
                                                                    "id",
                                                                    "manufacturer"
                                                                ],
                                                                "x-apifox-orders": [
                                                                    "description",
                                                                    "id",
                                                                    "manufacturer",
                                                                    "manufacturer_code"
                                                                ],
                                                                "x-apifox-ignore-properties": []
                                                            }
                                                        },
                                                        "C->S": {
                                                            "type": "array",
                                                            "items": {
                                                                "type": "object",
                                                                "properties": {
                                                                    "description": {
                                                                        "type": "string"
                                                                    },
                                                                    "id": {
                                                                        "type": "integer"
                                                                    },
                                                                    "manufacturer": {
                                                                        "type": "boolean"
                                                                    },
                                                                    "manufacturer_code": {
                                                                        "type": "integer"
                                                                    }
                                                                },
                                                                "required": [
                                                                    "id",
                                                                    "manufacturer"
                                                                ],
                                                                "x-apifox-orders": [
                                                                    "description",
                                                                    "id",
                                                                    "manufacturer",
                                                                    "manufacturer_code"
                                                                ],
                                                                "x-apifox-ignore-properties": []
                                                            }
                                                        }
                                                    },
                                                    "required": [
                                                        "S->C",
                                                        "C->S"
                                                    ],
                                                    "x-apifox-orders": [
                                                        "S->C",
                                                        "C->S"
                                                    ],
                                                    "x-apifox-ignore-properties": []
                                                },
                                                "id": {
                                                    "type": "integer"
                                                },
                                                "manufacturer": {
                                                    "type": "boolean"
                                                },
                                                "manufacturer_code": {
                                                    "type": "integer"
                                                },
                                                "name": {
                                                    "type": "string"
                                                }
                                            },
                                            "required": [
                                                "attributes",
                                                "commands",
                                                "id",
                                                "manufacturer",
                                                "name"
                                            ],
                                            "x-apifox-orders": [
                                                "attributes",
                                                "commands",
                                                "id",
                                                "manufacturer",
                                                "manufacturer_code",
                                                "name"
                                            ],
                                            "x-apifox-ignore-properties": []
                                        }
                                    },
                                    "device_id": {
                                        "type": "integer"
                                    },
                                    "device_version": {
                                        "type": "integer"
                                    },
                                    "id": {
                                        "type": "integer"
                                    },
                                    "profile_id": {
                                        "type": "integer"
                                    },
                                    "server_clusters": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "attributes": {
                                                    "type": "array",
                                                    "items": {
                                                        "type": "object",
                                                        "properties": {
                                                            "default": {
                                                                "oneOf": [
                                                                    {
                                                                        "type": "string"
                                                                    },
                                                                    {
                                                                        "type": "integer"
                                                                    }
                                                                ]
                                                            },
                                                            "id": {
                                                                "type": "integer"
                                                            },
                                                            "length": {
                                                                "type": "integer"
                                                            },
                                                            "manufacturer": {
                                                                "type": "boolean"
                                                            },
                                                            "manufacturer_code": {
                                                                "type": "integer"
                                                            },
                                                            "name": {
                                                                "type": "string"
                                                            },
                                                            "type": {
                                                                "type": "string"
                                                            },
                                                            "writable": {
                                                                "type": "boolean"
                                                            }
                                                        },
                                                        "required": [
                                                            "default",
                                                            "id",
                                                            "manufacturer",
                                                            "type",
                                                            "writable"
                                                        ],
                                                        "x-apifox-orders": [
                                                            "default",
                                                            "id",
                                                            "length",
                                                            "manufacturer",
                                                            "manufacturer_code",
                                                            "name",
                                                            "type",
                                                            "writable"
                                                        ],
                                                        "x-apifox-ignore-properties": []
                                                    }
                                                },
                                                "commands": {
                                                    "type": "object",
                                                    "properties": {
                                                        "S->C": {
                                                            "type": "array",
                                                            "items": {
                                                                "type": "object",
                                                                "properties": {
                                                                    "description": {
                                                                        "type": "string"
                                                                    },
                                                                    "id": {
                                                                        "type": "integer"
                                                                    },
                                                                    "manufacturer": {
                                                                        "type": "boolean"
                                                                    },
                                                                    "manufacturer_code": {
                                                                        "type": "integer"
                                                                    }
                                                                },
                                                                "required": [
                                                                    "id",
                                                                    "manufacturer"
                                                                ],
                                                                "x-apifox-orders": [
                                                                    "description",
                                                                    "id",
                                                                    "manufacturer",
                                                                    "manufacturer_code"
                                                                ],
                                                                "x-apifox-ignore-properties": []
                                                            }
                                                        },
                                                        "C->S": {
                                                            "type": "array",
                                                            "items": {
                                                                "type": "object",
                                                                "properties": {
                                                                    "description": {
                                                                        "type": "string"
                                                                    },
                                                                    "id": {
                                                                        "type": "integer"
                                                                    },
                                                                    "manufacturer": {
                                                                        "type": "boolean"
                                                                    },
                                                                    "manufacturer_code": {
                                                                        "type": "integer"
                                                                    }
                                                                },
                                                                "required": [
                                                                    "id",
                                                                    "manufacturer"
                                                                ],
                                                                "x-apifox-orders": [
                                                                    "description",
                                                                    "id",
                                                                    "manufacturer",
                                                                    "manufacturer_code"
                                                                ],
                                                                "x-apifox-ignore-properties": []
                                                            }
                                                        }
                                                    },
                                                    "required": [
                                                        "S->C",
                                                        "C->S"
                                                    ],
                                                    "x-apifox-orders": [
                                                        "S->C",
                                                        "C->S"
                                                    ],
                                                    "x-apifox-ignore-properties": []
                                                },
                                                "id": {
                                                    "type": "integer"
                                                },
                                                "manufacturer": {
                                                    "type": "boolean"
                                                },
                                                "manufacturer_code": {
                                                    "type": "integer"
                                                },
                                                "name": {
                                                    "type": "string"
                                                }
                                            },
                                            "required": [
                                                "attributes",
                                                "commands",
                                                "id",
                                                "manufacturer"
                                            ],
                                            "x-apifox-orders": [
                                                "attributes",
                                                "commands",
                                                "id",
                                                "manufacturer",
                                                "manufacturer_code",
                                                "name"
                                            ],
                                            "x-apifox-ignore-properties": []
                                        }
                                    }
                                },
                                "x-apifox-orders": [
                                    "client_clusters",
                                    "device_id",
                                    "device_version",
                                    "id",
                                    "profile_id",
                                    "server_clusters"
                                ],
                                "x-apifox-ignore-properties": []
                            }
                        },
                        "node": {
                            "type": "object",
                            "properties": {
                                "device_type": {
                                    "type": "string"
                                },
                                "manufacturer_code": {
                                    "type": "integer"
                                },
                                "radio_power": {
                                    "type": "integer"
                                }
                            },
                            "required": [
                                "device_type",
                                "manufacturer_code",
                                "radio_power"
                            ],
                            "x-apifox-orders": [
                                "device_type",
                                "manufacturer_code",
                                "radio_power"
                            ],
                            "x-apifox-ignore-properties": []
                        }
                    },
                    "required": [
                        "endpoints",
                        "node"
                    ],
                    "x-apifox-orders": [
                        "endpoints",
                        "node"
                    ],
                    "x-apifox-ignore-properties": []
                }
            },
            "required": [
                "filename",
                "config"
            ],
            "x-apifox-orders": [
                "filename",
                "config"
            ],
            "x-apifox-ignore-properties": []
        }

        @exception
        def handle():
            try:
                validate(instance=request.get_json(), schema=schema,
                         format_checker=draft7_format_checker)
            except Exception as e:
                raise InvalidPayload(repr(e))
            result, error = config_validation(request.get_json()['config'])
            if not result:
                raise InvalidPayload(error)
            filename = request.get_json()['filename']
            with open(os.path.join(base_dir, './files') + '/' + filename, 'w+') as f:
                yaml.safe_dump(request.get_json()['config'], f)
            return {}

        return handle()


class ConfigFilesResource(Resource):
    """
    /configs/files
    """

    def get(self):
        """
        获取本地模板列表，并显示缩略信息，包含device_type, endpoint内容
        :return:
        """

        @exception
        def handle():
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
            return data

        return handle()

    def post(self):
        """
        上传模板文件
        :return:
        """

        @exception
        def handle():
            parser = reqparse.RequestParser()
            parser.add_argument('file', type=werkzeug.datastructures.FileStorage, location='files')
            args = parser.parse_args()
            content = args.get('file')
            files = request.files.getlist('file')
            for file in files:
                try:
                    y = yaml.safe_load(file.read())
                    validate(instance={'config': y}, schema=config_schema,
                             format_checker=draft7_format_checker)
                except Exception as e:
                    raise InvalidPayload(repr(e))
                    # 验证文件每个字段的值是否符合要求
                result, error = config_validation(y)
                if not result:
                    raise InvalidPayload(error)
                filename = secure_filename(file.filename)
                file.seek(0)
                file.save(os.path.join('./files', filename))
            return {}

        return handle()

    def delete(self):
        """
        删除所有模板文件
        :return:
        """

        @exception
        def handle():
            for root, dirs, files in os.walk(os.path.join(base_dir, './files')):
                for file in files:
                    if os.path.isfile(root + '/' + file):
                        os.remove(root + '/' + file)
            return {}

        return handle()


class ConfigFileResource(Resource):
    """
    /configs/files/<filename>
    """

    def get(self, file):
        """
        获取模板文件
        """

        @exception
        def handle():
            print("filename:", file)
            try:
                with open(os.path.join(base_dir, './files') + '/' + file, 'r') as f:
                    try:
                        y = yaml.safe_load(f.read())
                    except Exception as e:
                        raise InvalidPayload(repr(e))
                    return {
                        'filename': file,
                        'config': y
                    }
            except FileNotFoundError:
                raise NotFound(file)

        return handle()

    def delete(self, file):
        """
        删除当前模板文件
        :return:
        """

        @exception
        def handle():
            if os.path.isfile(os.path.join(base_dir, './files') + '/' + file):
                os.remove(os.path.join(base_dir, './files') + '/' + file)
            return {}

        return handle()


class ConfigDevicesResource(Resource):
    """
    /configs/devices
    """

    def put(self):
        schema = {
            "type": "object",
            "properties": {
                "filename": {
                    "type": "string"
                },
                "config": {
                    "type": "object",
                    "properties": {
                        "endpoints": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "client_clusters": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "attributes": {
                                                    "type": "array",
                                                    "items": {
                                                        "type": "object",
                                                        "properties": {
                                                            "default": {
                                                                "oneOf": [
                                                                    {
                                                                        "type": "string"
                                                                    },
                                                                    {
                                                                        "type": "integer"
                                                                    }
                                                                ]
                                                            },
                                                            "id": {
                                                                "type": "integer"
                                                            },
                                                            "length": {
                                                                "type": "integer"
                                                            },
                                                            "manufacturer": {
                                                                "type": "boolean"
                                                            },
                                                            "manufacturer_code": {
                                                                "type": "integer"
                                                            },
                                                            "name": {
                                                                "type": "string"
                                                            },
                                                            "type": {
                                                                "type": "string"
                                                            },
                                                            "writable": {
                                                                "type": "boolean"
                                                            }
                                                        },
                                                        "required": [
                                                            "default",
                                                            "id",
                                                            "manufacturer",
                                                            "type",
                                                            "writable"
                                                        ],
                                                        "x-apifox-orders": [
                                                            "default",
                                                            "id",
                                                            "length",
                                                            "manufacturer",
                                                            "manufacturer_code",
                                                            "name",
                                                            "type",
                                                            "writable"
                                                        ],
                                                        "x-apifox-ignore-properties": []
                                                    }
                                                },
                                                "commands": {
                                                    "type": "object",
                                                    "properties": {
                                                        "S->C": {
                                                            "type": "array",
                                                            "items": {
                                                                "type": "object",
                                                                "properties": {
                                                                    "description": {
                                                                        "type": "string"
                                                                    },
                                                                    "id": {
                                                                        "type": "integer"
                                                                    },
                                                                    "manufacturer": {
                                                                        "type": "boolean"
                                                                    },
                                                                    "manufacturer_code": {
                                                                        "type": "integer"
                                                                    }
                                                                },
                                                                "required": [
                                                                    "id",
                                                                    "manufacturer"
                                                                ],
                                                                "x-apifox-orders": [
                                                                    "description",
                                                                    "id",
                                                                    "manufacturer",
                                                                    "manufacturer_code"
                                                                ],
                                                                "x-apifox-ignore-properties": []
                                                            }
                                                        },
                                                        "C->S": {
                                                            "type": "array",
                                                            "items": {
                                                                "type": "object",
                                                                "properties": {
                                                                    "description": {
                                                                        "type": "string"
                                                                    },
                                                                    "id": {
                                                                        "type": "integer"
                                                                    },
                                                                    "manufacturer": {
                                                                        "type": "boolean"
                                                                    },
                                                                    "manufacturer_code": {
                                                                        "type": "integer"
                                                                    }
                                                                },
                                                                "required": [
                                                                    "id",
                                                                    "manufacturer"
                                                                ],
                                                                "x-apifox-orders": [
                                                                    "description",
                                                                    "id",
                                                                    "manufacturer",
                                                                    "manufacturer_code"
                                                                ],
                                                                "x-apifox-ignore-properties": []
                                                            }
                                                        }
                                                    },
                                                    "required": [
                                                        "S->C",
                                                        "C->S"
                                                    ],
                                                    "x-apifox-orders": [
                                                        "S->C",
                                                        "C->S"
                                                    ],
                                                    "x-apifox-ignore-properties": []
                                                },
                                                "id": {
                                                    "type": "integer"
                                                },
                                                "manufacturer": {
                                                    "type": "boolean"
                                                },
                                                "manufacturer_code": {
                                                    "type": "integer"
                                                },
                                                "name": {
                                                    "type": "string"
                                                }
                                            },
                                            "required": [
                                                "attributes",
                                                "commands",
                                                "id",
                                                "manufacturer",
                                                "name"
                                            ],
                                            "x-apifox-orders": [
                                                "attributes",
                                                "commands",
                                                "id",
                                                "manufacturer",
                                                "manufacturer_code",
                                                "name"
                                            ],
                                            "x-apifox-ignore-properties": []
                                        }
                                    },
                                    "device_id": {
                                        "type": "integer"
                                    },
                                    "device_version": {
                                        "type": "integer"
                                    },
                                    "id": {
                                        "type": "integer"
                                    },
                                    "profile_id": {
                                        "type": "integer"
                                    },
                                    "server_clusters": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "attributes": {
                                                    "type": "array",
                                                    "items": {
                                                        "type": "object",
                                                        "properties": {
                                                            "default": {
                                                                "oneOf": [
                                                                    {
                                                                        "type": "string"
                                                                    },
                                                                    {
                                                                        "type": "integer"
                                                                    }
                                                                ]
                                                            },
                                                            "id": {
                                                                "type": "integer"
                                                            },
                                                            "length": {
                                                                "type": "integer"
                                                            },
                                                            "manufacturer": {
                                                                "type": "boolean"
                                                            },
                                                            "manufacturer_code": {
                                                                "type": "integer"
                                                            },
                                                            "name": {
                                                                "type": "string"
                                                            },
                                                            "type": {
                                                                "type": "string"
                                                            },
                                                            "writable": {
                                                                "type": "boolean"
                                                            }
                                                        },
                                                        "required": [
                                                            "default",
                                                            "id",
                                                            "manufacturer",
                                                            "type",
                                                            "writable"
                                                        ],
                                                        "x-apifox-orders": [
                                                            "default",
                                                            "id",
                                                            "length",
                                                            "manufacturer",
                                                            "manufacturer_code",
                                                            "name",
                                                            "type",
                                                            "writable"
                                                        ],
                                                        "x-apifox-ignore-properties": []
                                                    }
                                                },
                                                "commands": {
                                                    "type": "object",
                                                    "properties": {
                                                        "S->C": {
                                                            "type": "array",
                                                            "items": {
                                                                "type": "object",
                                                                "properties": {
                                                                    "description": {
                                                                        "type": "string"
                                                                    },
                                                                    "id": {
                                                                        "type": "integer"
                                                                    },
                                                                    "manufacturer": {
                                                                        "type": "boolean"
                                                                    },
                                                                    "manufacturer_code": {
                                                                        "type": "integer"
                                                                    }
                                                                },
                                                                "required": [
                                                                    "id",
                                                                    "manufacturer"
                                                                ],
                                                                "x-apifox-orders": [
                                                                    "description",
                                                                    "id",
                                                                    "manufacturer",
                                                                    "manufacturer_code"
                                                                ],
                                                                "x-apifox-ignore-properties": []
                                                            }
                                                        },
                                                        "C->S": {
                                                            "type": "array",
                                                            "items": {
                                                                "type": "object",
                                                                "properties": {
                                                                    "description": {
                                                                        "type": "string"
                                                                    },
                                                                    "id": {
                                                                        "type": "integer"
                                                                    },
                                                                    "manufacturer": {
                                                                        "type": "boolean"
                                                                    },
                                                                    "manufacturer_code": {
                                                                        "type": "integer"
                                                                    }
                                                                },
                                                                "required": [
                                                                    "id",
                                                                    "manufacturer"
                                                                ],
                                                                "x-apifox-orders": [
                                                                    "description",
                                                                    "id",
                                                                    "manufacturer",
                                                                    "manufacturer_code"
                                                                ],
                                                                "x-apifox-ignore-properties": []
                                                            }
                                                        }
                                                    },
                                                    "required": [
                                                        "S->C",
                                                        "C->S"
                                                    ],
                                                    "x-apifox-orders": [
                                                        "S->C",
                                                        "C->S"
                                                    ],
                                                    "x-apifox-ignore-properties": []
                                                },
                                                "id": {
                                                    "type": "integer"
                                                },
                                                "manufacturer": {
                                                    "type": "boolean"
                                                },
                                                "manufacturer_code": {
                                                    "type": "integer"
                                                },
                                                "name": {
                                                    "type": "string"
                                                }
                                            },
                                            "required": [
                                                "attributes",
                                                "commands",
                                                "id",
                                                "manufacturer",
                                                "name"
                                            ],
                                            "x-apifox-orders": [
                                                "attributes",
                                                "commands",
                                                "id",
                                                "manufacturer",
                                                "manufacturer_code",
                                                "name"
                                            ],
                                            "x-apifox-ignore-properties": []
                                        }
                                    }
                                },
                                "x-apifox-orders": [
                                    "client_clusters",
                                    "device_id",
                                    "device_version",
                                    "id",
                                    "profile_id",
                                    "server_clusters"
                                ],
                                "required": [
                                    "client_clusters",
                                    "device_id",
                                    "device_version",
                                    "id",
                                    "profile_id",
                                    "server_clusters"
                                ],
                                "x-apifox-ignore-properties": []
                            }
                        },
                        "node": {
                            "type": "object",
                            "properties": {
                                "device_type": {
                                    "type": "string"
                                },
                                "manufacturer_code": {
                                    "type": "integer"
                                },
                                "radio_power": {
                                    "type": "integer"
                                }
                            },
                            "required": [
                                "device_type",
                                "manufacturer_code",
                                "radio_power"
                            ],
                            "x-apifox-orders": [
                                "device_type",
                                "manufacturer_code",
                                "radio_power"
                            ],
                            "x-apifox-ignore-properties": []
                        }
                    },
                    "required": [
                        "endpoints",
                        "node"
                    ],
                    "x-apifox-orders": [
                        "endpoints",
                        "node"
                    ],
                    "x-apifox-ignore-properties": []
                },
                "devices": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    }
                }
            },
            "x-apifox-orders": [
                "filename",
                "config",
                "devices"
            ],
            "required": [
                "devices"
            ],
            "x-apifox-ignore-properties": []
        }

        @exception
        def handle():
            try:
                validate(instance=request.get_json(), schema=schema,
                         format_checker=draft7_format_checker)
            except Exception as e:
                raise InvalidPayload(repr(e))
            devices = request.get_json().get('devices')
            filename = request.get_json().get('filename')
            config = request.get_json().get('config')
            if filename:
                path = os.path.join(base_dir, './files') + '/' + filename
                try:
                    with open(path, 'r') as f:
                        config = yaml.safe_load(f.read())
                except Exception as e:
                    raise NotFound('filename')

            result, error = config_validation(config)
            if not result:
                raise InvalidPayload(error)

            simulators = {}
            for mac in devices:
                device = DBDevice(mac=mac).retrieve()
                if not device:
                    raise DeviceNotFound(mac)
                else:
                    device = device[0]
                if not device.get('connected'):
                    raise DeviceOffline(mac)
                simulator = device.get('ip')
                if simulator not in simulators:
                    simulators.update({simulator: [mac]})
                else:
                    simulators[simulator].append(mac)

            for simulator, devices in simulators.items():
                result = send_command(ip=simulator, command={
                    'config': {
                        'config': config,
                        'devices': devices
                    }
                })
                if result != {}:
                    return result
            return {}
        return handle()
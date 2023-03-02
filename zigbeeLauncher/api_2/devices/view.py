import os

import rapidjson
import werkzeug
import yaml
from flask import jsonify, render_template, request
from flask_restful import Api, Resource, reqparse
from jsonschema import validate
from jsonschema._format import draft7_format_checker

from zigbeeLauncher.database.interface import DBDevice
from zigbeeLauncher.logging import flaskLogger as logger
from ..json_schemas import config_schema

from ..util import check_device_exist, check_device_state, config_validation, send_command
from ... import base_dir
from ...dongle.dongle import Dongle
from ...exceptions import exception, DeviceOffline, InvalidPayload, Unsupported, DeviceNotFound, DeviceNotReady, \
    NotFound


class DevicesResource(Resource):
    """
    /devices
    """

    def get(self):
        @exception
        def handle():
            paras = request.args
            devices = DBDevice(**paras).retrieve()
            return devices

        return handle()


class DeviceResource(Resource):
    """
    /devices/<mac>
    """

    def get(self, mac):
        @exception
        def handle():
            device = DBDevice(mac=mac).retrieve()
            if not device:
                raise DeviceNotFound(mac)
            else:
                return device[0]

        return handle()

    def put(self, mac):
        commands = ['identify', 'reset', 'label']
        schema = {
            "type": "object",
            "properties": {
                "identify": {
                    "type": "object",
                    "properties": {},
                    "description": "identify request"
                },
                "reset": {
                    "type": "object",
                    "properties": {},
                    "description": "reset request"
                },
                "label": {
                    "type": "object",
                    "properties": {
                        "data": {
                            "type": "string",
                            "description": "label"
                        }
                    },
                    "description": "label modification request",
                    "required": [
                        "data"
                    ]
                }
            }
        }

        @exception
        def handle():
            device = DBDevice(mac=mac).retrieve()
            if not device:
                raise DeviceNotFound(mac)
            else:
                device = device[0]

            if not device.get('connected'):
                raise DeviceOffline(mac)
            try:
                validate(instance=request.get_json(), schema=schema,
                         format_checker=draft7_format_checker)
            except Exception as e:
                raise InvalidPayload(e.description)
            for k, v in request.get_json().items():
                if k not in commands:
                    raise Unsupported(k)
                return send_command(ip=device.get('ip'), mac=mac, command={k: v})

        return handle()


class DeviceConfigResource(Resource):
    """
    /devices/<mac>/config
    """

    def get(self, mac):
        @exception
        def handle():
            device = DBDevice(mac=mac).retrieve()
            if not device:
                raise DeviceNotFound(mac)
            else:
                device = device[0]
                if not device.get('connected'):
                    raise DeviceOffline(mac)
                if not device.get('configured'):
                    raise DeviceNotReady(mac)
                return send_command(ip=device.get('ip'), mac=mac, command={'get_config': {}})

        return handle()

    def put(self, mac):
        schema = {
            "type": "object",
            "properties": {
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
                "config"
            ],
            "x-apifox-orders": [
                "config"
            ],
            "x-apifox-ignore-properties": []
        }

        @exception
        def handle():
            device = DBDevice(mac=mac).retrieve()
            if not device:
                raise DeviceNotFound(mac)
            else:
                device = device[0]
                if not device.get('connected'):
                    raise DeviceOffline(mac)
                if device.get('state') == Dongle.DongleState.CONFIGURING:
                    raise DeviceNotReady(mac)
                try:
                    validate(instance=request.get_json(), schema=schema,
                             format_checker=draft7_format_checker)
                except Exception as e:
                    raise InvalidPayload(e.description)
                result, error = config_validation(request.get_json()['config'])
                if not result:
                    raise InvalidPayload(error)

                return send_command(ip=device.get('ip'), mac=mac, command=request.get_json())

        return handle()

    def post(self, mac):
        schema = {
            "type": "object",
            "properties": {
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
                "config"
            ],
            "x-apifox-orders": [
                "config"
            ],
            "x-apifox-ignore-properties": []
        }

        @exception
        def handle():
            parser = reqparse.RequestParser()
            parser.add_argument('file', type=werkzeug.datastructures.FileStorage, location='files')
            args = parser.parse_args()
            content = args.get('file')
            if not content:
                raise NotFound("file not found")
            device = DBDevice(mac=mac).retrieve()
            if not device:
                raise DeviceNotFound(mac)
            else:
                device = device[0]
                if not device.get('connected'):
                    raise DeviceOffline(mac)
                if device.get('state') == Dongle.DongleState.CONFIGURING:
                    raise DeviceNotReady(mac)
                try:
                    y = yaml.safe_load(content.read())
                    validate(instance={'config': y}, schema=schema,
                             format_checker=draft7_format_checker)
                except Exception as e:
                    raise InvalidPayload(e.description)
                result, error = config_validation(y)
                if not result:
                    raise InvalidPayload(error)
                return send_command(ip=device.get('ip'), mac=mac, command={'config': y})

        return handle()
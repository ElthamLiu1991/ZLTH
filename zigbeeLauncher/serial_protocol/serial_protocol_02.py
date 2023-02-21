import sys
from binascii import unhexlify

from zigbeeLauncher.serial_protocol import response
from zigbeeLauncher.serial_protocol.serial_protocol import encode, big_small_end_convert, to_hex, \
    big_small_end_convert_to_int, big_small_end_convert_from_int, ack, signed_to_unsigned, unsigned_to_signed, \
    from_string
from zigbeeLauncher.logging import dongleLogger as logger
from zigbeeLauncher.zigbee.data_type import get_bytes, data_type_value_table, data_type_name_table, data_type_table

serial_protocol_schema_0200 = {
    'device_type':{
        'type': 'integer',
        'length': 1,
        'enumerate':{
            'coordinator': 0x00,
            'router': 0x01,
            'end_device': 0x02,
            'sleepy_end_device': 0x03,
            'unknown': 0xFF
        }
    },
    'radio_power':{
        'type': 'integer',
        'length': 1
    },
    'manufacturer_code':{
        'type': 'integer',
        'length': 2
    }
}
serial_protocol_schema_0202 = {
    'device_type': {
        'type': 'integer',
        'length': 1,
        'enumerate': {
            0x00: 'coordinator',
            0x01: 'router',
            0x02: 'end_device',
            0x03: 'sleepy_end_device',
            0xFF: 'unknown'
        }
    },
    'radio_power': {
        'type': 'integer',
        'length': 1
    },
    'manufacturer_code': {
        'type': 'integer',
        'length': 2
    }
}
serial_protocol_schema_0205 = {
    'number_of_endpoints': {
        'type': 'integer',
        'length': 1
    },
    'endpoints': {
        'type': 'array',
        'length': 'number_of_endpoints',
        'object': {
            'id': {
                'type': 'integer',
                'length': 1
            }
        }
    }
}
serial_protocol_schema_0207 = {
    'id': {
        'type': 'integer',
        'length': 1
    },
    'profile_id': {
        'type': 'integer',
        'length': 2
    },
    'device_id': {
        'type': 'integer',
        'length': 2
    },
    'device_version': {
        'type': 'integer',
        'length': 1
    },
    'number_of_server_cluster': {
        'type': 'integer',
        'length': 1
    },
    'number_of_client_cluster': {
        'type': 'integer',
        'length': 1
    },
    'server_clusters': {
        'type': 'array',
        'length': "number_of_server_cluster",
        'object': {
            'id': {
                'type': 'integer',
                'length': 2
            },
            'manufacturer_code': {
                'type': 'integer',
                'length': 2
            }
        }
    },
    'client_clusters': {
        'type': 'array',
        'length': "number_of_client_cluster",
        'object': {
            'id': {
                'type': 'integer',
                'length': 2
            },
            'manufacturer_code': {
                'type': 'integer',
                'length': 2
            }
        }
    }
}
serial_protocol_schema_020A = {
    'endpoint_id': {
        'type': 'integer',
        'length': 1
    },
    'cluster_id': {
        'type': 'integer',
        'length': 2
    },
    'manufacturer_code': {
        'type': 'integer',
        'length': 2
    },
    'server': {
        'type': 'integer',
        'length': 1
    },
    'total_number_of_attributes': {
        'type': 'integer',
        'length': 1
    },
    'remain_number_of_attributes': {
        'type': 'integer',
        'length': 1
    },
    'number_of_attributes': {
        'type': 'integer',
        'length': 1
    },
    'attributes': {
        'type': 'array',
        'length': 'number_of_attributes',
        'object': {
            'id': {
                'type': 'integer',
                'length': 2
            },
            'manufacturer_code': {
                'type': 'integer',
                'length': 2
            },
            'type': {
                'type': 'integer',
                'length': 1,
                'enumerate': data_type_name_table
            },
            'attribute_property_bitmask': {
                'type': 'integer',
                'length': 1
            },
            'attribute_value_max_length': {
                'type': 'integer',
                'length': 1
            },
            'default': {
                'type': 'type',
                'length': 'attribute_value_max_length'
            }
        }
    }
}
serial_protocol_schema_020C = {
    'endpoint':{
        'type': 'integer',
        'length': 1
    },
    'cluster':{
        'type': 'integer',
        'length':2
    },
    'server':{
        'type': 'integer',
        'length': 1
    },
    'attribute':{
        'type': 'integer',
        'length': 2
    },
    'manufacturer_code':{
        'type': 'integer',
        'length': 2
    },
    'attribute_property_bitmask':{
        'type': 'integer',
        'length': 1
    },
    'type': {
        'type': 'integer',
        'length': 1,
        'enumerate': data_type_name_table
    },
    'value': {
        'type': 'type'
    }
}
serial_protocol_schema_0211 = {
    'endpoint_id': {
        'type': 'integer',
        'length': 1
    },
    'cluster_id': {
        'type': 'integer',
        'length': 2
    },
    'manufacturer_code': {
        'type': 'integer',
        'length': 2
    },
    'server': {
        'type': 'integer',
        'length': 1
    },
    'total_number_of_commands': {
        'type': 'integer',
        'length': 1
    },
    'remains_number_of_commands': {
        'type': 'integer',
        'length': 1
    },
    'number_of_commands': {
        'type': 'integer',
        'length': 1
    },
    'commands': {
        'type': 'array',
        'length': 'number_of_commands',
        'object': {
            'id': {
                'type': 'integer',
                'length': 1
            },
            'mask': {
                'type': 'integer',
                'length': 1,
                'enumerate': {
                    0x00: 'C->S',
                    0x01: 'S->C'
                }
            },
            'manufacturer_code':{
                'type': 'integer',
                'length': 2
            }
        }
    }
}
zigbee_config_command = '02'

node_info_write = '00'
node_info_request = '01'
node_info_response = '02'
add_endpoint = '03'
endpoint_list_request = "04"
endpoint_list_response = "05"
endpoint_descriptor_request = '06'
endpoint_descriptor_response = '07'
add_attributes_to_cluster = '08'
attribute_list_request = '09'
attribute_list_response = '0A'
attribute_request = '0B'
attribute_response = '0C'
attribute_write_request = '0D'
attribute_default_value_write = '0E'
add_supported_command_to_cluster = '0F'
supported_commands_list_request = '10'
supported_commands_list_response = '11'

device_type = {
    "coordinator": "00",
    "router": "01",
    "end_device": "02",
    "sleepy_end_device": "03",
    "unknown": "FF"
}


def node_info_write_handle(seq, payload=None):
    logger.info("function:%s, seq:%d", sys._getframe().f_code.co_name, seq)
    """
    :param payload:
        {
            "device_type":'router',
            "radio_power": 10,
            "manufacturer_code": 1234
        }
    :return:
    """
    data = ""
    type = payload['device_type']
    if type in device_type:
        data = data + device_type[type]
    else:
        data = data + 'FF'
    data = data + to_hex(payload['radio_power'])
    data = data + big_small_end_convert_from_int(payload['manufacturer_code'])
    return encode(seq, zigbee_config_command + node_info_write, data)


def node_info_request_handle(seq, payload=None):
    logger.info("function:%s, seq:%d", sys._getframe().f_code.co_name, seq)
    return encode(seq, zigbee_config_command + node_info_request, None)


@response.cmd(zigbee_config_command + node_info_response, serial_protocol_schema_0202)
def node_info_response_handle(sequence, dongle, protocol):
    rsp = {'node': protocol.__dict__}
    dongle.response(sequence, payload=rsp)


def add_endpoint_handle(seq, payload=None):
    logger.info("function:%s, seq:%d", sys._getframe().f_code.co_name, seq)
    """

    :param payload:
        {
            "id": 1,
            "profile_id": 1234,
            "device_id": 1234,
            "device_version": 1,
            "server_clusters":[
                {
                    "id": 1234,
                    'manufacturer": true,
                    "manufacturer_code": 1234
                }
            ],
            "client_clusters":[
                {
                    "id": 1234,
                    'manufacturer": false
                }
            ]
        }
    :return:
    """
    data = ""
    data = data + to_hex(payload['id'])
    data = data + big_small_end_convert_from_int(payload['profile_id'])
    data = data + big_small_end_convert_from_int(payload['device_id'])
    data = data + to_hex(payload['device_version'])
    data = data + to_hex(len(payload['server_clusters']))
    data = data + to_hex(len(payload['client_clusters']))
    for cluster in payload['server_clusters']:
        data = data + big_small_end_convert_from_int(cluster['id'])
        if not cluster['manufacturer']:
            data = data + '0000'
        else:
            data = data + big_small_end_convert_from_int(cluster['manufacturer_code'])
    for cluster in payload['client_clusters']:
        data = data + big_small_end_convert_from_int(cluster['id'])
        if not cluster['manufacturer']:
            data = data + '0000'
        else:
            data = data + big_small_end_convert_from_int(cluster['manufacturer_code'])
    return encode(seq, zigbee_config_command + add_endpoint, data)


def endpoint_list_request_handle(seq, payload=None):
    logger.info("function:%s, seq:%d", sys._getframe().f_code.co_name, seq)
    return encode(seq, zigbee_config_command + endpoint_list_request, None)


@response.cmd(zigbee_config_command + endpoint_list_response, serial_protocol_schema_0205)
def endpoint_list_response_handle(sequence, dongle, protocol):
    endpoints = []
    for endpoint in protocol.endpoints:
        endpoints.append({'id': endpoint.id})
    dongle.response(sequence, payload={'endpoints': endpoints})


def endpoint_descriptor_request_handle(seq, payload):
    logger.info("function:%s, seq:%d", sys._getframe().f_code.co_name, seq)
    endpoint = to_hex(payload)
    return encode(seq, zigbee_config_command + endpoint_descriptor_request, endpoint)


@response.cmd(zigbee_config_command + endpoint_descriptor_response, serial_protocol_schema_0207)
def endpoint_descriptor_response_handle(sequence, dongle, protocol):
    endpoint = protocol.__dict__
    server_clusters = []
    client_clusters = []
    for cluster in protocol.server_clusters:
        _cluster = cluster.__dict__
        if cluster.manufacturer_code == 0:
            _cluster['manufacturer'] = False
            del _cluster['manufacturer_code']
        else:
            _cluster['manufacturer'] = True
        _cluster['attributes'] = []
        _cluster['commands'] = {'C->S': [], 'S->C': []}
        server_clusters.append(_cluster)
    for cluster in protocol.client_clusters:
        _cluster = cluster.__dict__
        if cluster.manufacturer_code == 0:
            _cluster['manufacturer'] = False
            del _cluster['manufacturer_code']
        else:
            _cluster['manufacturer'] = True
        _cluster['attributes'] = []
        _cluster['commands'] = {'C->S': [], 'S->C': []}
        client_clusters.append(_cluster)
    endpoint['server_clusters'] = server_clusters
    endpoint['client_clusters'] = client_clusters
    del endpoint['number_of_server_cluster']
    del endpoint['number_of_client_cluster']
    dongle.response(sequence, payload=endpoint)


def add_attributes_to_cluster_handle(seq, payload, config):
    logger.info("function:%s, seq:%d", sys._getframe().f_code.co_name, seq)
    """
    serial package maximum size: 200
    如果该cluster下面的attribute长度超过200，需要分包进行处理
    :param payload:
        {
            "endpoint_id": 1,
            "cluster_id": 1234,
            "manufacturer_code":1234,
            "server": True,
            "attributes":[
                {
                    "id": 1234,
                    "manufacturer": true,
                    "manufacturer_code": 1234,(optional)
                    "type":"uint16",
                    "writable": False,
                    "default": 1,
                    "length": 32(optional)
                }
            ]
        }
    :return:
    """
    head = ""
    head = head + to_hex(payload['endpoint_id'])
    head = head + big_small_end_convert_from_int(payload['cluster_id'])
    head = head + big_small_end_convert_from_int(payload['manufacturer_code'])
    head = head + to_hex(int(payload['server']))
    # count = len(payload['attributes'])
    # data = data + to_hex(count)
    data = ""
    count = 0
    for attribute in payload['attributes']:
        logger.info("write attribute:%d", attribute['id'])
        tmp = ''
        tmp = tmp + big_small_end_convert_from_int(attribute['id'])
        if attribute['manufacturer']:
            tmp = tmp + big_small_end_convert_from_int(attribute['manufacturer_code'])
        else:
            tmp = tmp + '0000'
        type_str = attribute['type']
        if type_str in data_type_value_table:
            type = data_type_value_table[type_str]
            tmp = tmp + to_hex(type)
        else:
            type = 0xFF
            tmp = tmp + 'FF'
        mask = 2
        if attribute['writable']:
            mask = mask + 1
        tmp = tmp + to_hex(mask)
        if 'length' in attribute:
            length = attribute['length']
            tmp = tmp + to_hex(length)
            value_length = len(attribute['default'])
            tmp = tmp + from_string(attribute['default'], value_length)
            # tmp = tmp + to_hex(length)
            # tmp = tmp + "".join(format(ord(c), "02X") for c in attribute['default'])
            if value_length < length:
                for i in range(length - value_length - 1):
                    tmp = tmp + '00'
            print(tmp)
        else:
            length = get_bytes(type)
            tmp = tmp + to_hex(length)
            default = attribute['default']
            if default < 0:
                # 将负数进行转换
                default = signed_to_unsigned(default, length)
            tmp = tmp + big_small_end_convert_from_int(default, length)
        if len(head) + 2 + len(data) + len(tmp) > 400:
            # 将该attribute放到下一个包
            if count == 0:
                count = 1
            config.count = count
            data = head + to_hex(count) + data
            print(data)
            return encode(seq, zigbee_config_command + add_attributes_to_cluster, data)
        data = data + tmp
        count = count + 1
    config.count = count
    data = head + to_hex(count) + data
    return encode(seq, zigbee_config_command + add_attributes_to_cluster, data)


def attribute_list_request_handle(seq, payload=None):
    logger.info("function:%s, seq:%d", sys._getframe().f_code.co_name, seq)
    """

    :param payload:
        {
            "endpoint_id": 1,
            "cluster_id": 1234,
            "manufacturer": false,
            'manufacturer_code":1234,
            "server": False
        }
    :return:
    """
    print(payload)
    data = ""
    data = data + to_hex(payload['endpoint_id'])
    data = data + big_small_end_convert_from_int(payload['cluster_id'])
    if payload['manufacturer']:
        data = data + big_small_end_convert_from_int(payload['manufacturer_code'])
    else:
        data = data + "0000"
    data = data + to_hex(int(payload['server']))

    return encode(seq, zigbee_config_command + attribute_list_request, data)


@response.cmd(zigbee_config_command + attribute_list_response, serial_protocol_schema_020A)
def attribute_list_response_handle(sequence, dongle, protocol):
    # ACK
    dongle.write(ack(zigbee_config_command + attribute_list_response, sequence))
    attributes = []
    for attribute in protocol.attributes:
        _attribute = attribute.__dict__
        if attribute.manufacturer_code == 0:
            _attribute['manufacturer'] = False
            if protocol.manufacturer_code != 0:
                _attribute['manufacturer'] = True
                _attribute['manufacturer_code'] = protocol.manufacturer_code
            else:
                del _attribute['manufacturer_code']
        else:
            _attribute['manufacturer'] = True
        if attribute.attribute_property_bitmask & 0x01:
            _attribute['writable'] = True
        else:
            _attribute['writable'] = False
        if isinstance(attribute.default, str):
            _attribute['length'] = attribute.attribute_value_max_length
        del _attribute['attribute_property_bitmask']
        del _attribute['attribute_value_max_length']
        attributes.append(_attribute)

    if sequence == dongle.config.seq:
        return
    if protocol.endpoint_id != dongle.config.endpoint_id:
        return
    if protocol.cluster_id != dongle.config.cluster_id:
        return
    if protocol.server != dongle.config.server:
        return
    if protocol.manufacturer_code == 0 and dongle.config.manufacturer:
        return
    if protocol.manufacturer_code != 0 and not dongle.config.manufacturer:
        return
    dongle.config.seq = sequence

    dongle.config.cluster['attributes'].extend(attributes)
    if protocol.remain_number_of_attributes == 0:
        dongle.config.next = True


def attribute_request_handle(seq, payload):
    logger.info("function:%s, seq:%d", sys._getframe().f_code.co_name, seq)
    """
        :param payload:
        {
            "endpoint":1,
            "cluster": 1234,
            "server":1,
            "attribute": 1234,
            "manufacturer": 1,
            "manufacturer_code":1234
        }
        :return:
        """
    data = ""
    data = data + to_hex(int(payload['endpoint']))
    data = data + big_small_end_convert_from_int(int(payload['cluster']), 2)
    data = data + to_hex(int(payload['server']))
    data = data + big_small_end_convert_from_int(int(payload['attribute']), 2)
    if bool(payload['manufacturer']):
        data = data + big_small_end_convert_from_int(int(payload['manufacturer_code']), 2)
    else:
        data = data + "0000"
    return encode(seq, zigbee_config_command + attribute_request, data)


@response.cmd(zigbee_config_command + attribute_response, serial_protocol_schema_020C)
def attribute_response_handle(sequence, dongle, protocol):
    dongle.write(ack(zigbee_config_command + attribute_response, sequence))
    """
    byte0: endpoint,
    byte1,2: cluster
    byte3: server/client
    byte4,5: attribute
    byte6,7: manufacturer_code
    byte8: attribute_property
    byte9: attribute_type,
    byte10..n: value
    """
    attribute = protocol.__dict__
    if protocol.manufacturer_code == 0:
        attribute['manufacturer'] = False
        del attribute['manufacturer_code']
    else:
        attribute['manufacturer'] = True
    if protocol.attribute_property_bitmask & 0x01:
        attribute['writable'] = True
    if protocol.server == 1:
        attribute['server'] = True
    else:
        attribute['server'] = False
    del attribute['attribute_property_bitmask']
    dongle.response(sequence, payload=attribute)


def attribute_write_request_handle(seq, payload):
    logger.info("function:%s, seq:%d", sys._getframe().f_code.co_name, seq)
    """
        :param payload:
        {
            "endpoint":1,
            "cluster": 1234,
            "server":true,
            "attribute": 1234,
            "manufacturer":false,
            "manufacturer_code":1234, optional
            "type": 'bool'
            "value": 1,
            "value": "this is a string",
            "length": 16, optional
        }
        :return:
        """
    data = ""
    data = data + to_hex(payload['endpoint'])
    data = data + big_small_end_convert_from_int(payload['cluster'], 2)
    data = data + to_hex(int(payload['server']))
    data = data + big_small_end_convert_from_int(payload['attribute'], 2)
    if 'manufacturer_code' not in payload:
        data = data + '0000'
    else:
        data = data + big_small_end_convert_from_int(payload['manufacturer_code'], 2)
    type = data_type_value_table[payload['type']]
    data = data + to_hex(type)

    length = data_type_table[type]
    value = payload['value']
    if isinstance(value, str):
        data = data + from_string(value, len(value))
        print(data)
        # data = data + to_hex(len(payload['value']))
        # data = data + "".join(format(ord(c), "02X") for c in payload['value'])
    else:
        if value < 0:
            value = signed_to_unsigned(value, length)
        data = data + big_small_end_convert_from_int(value, length)
    return encode(seq, zigbee_config_command + attribute_write_request, data)


def attribute_default_value_write_handle(seq, payload=None):
    logger.info("function:%s, seq:%d", sys._getframe().f_code.co_name, seq)
    return encode(seq, zigbee_config_command + attribute_default_value_write, None)


def add_supported_command_to_cluster_handle(seq, payload=None):
    logger.info("function:%s, seq:%d", sys._getframe().f_code.co_name, seq)
    """

    :param payload:
        {
            "endpoint_id": 1,
            "cluster_id": 1234,
            "manufacturer_code": 1234,
            "server": True,
            "commands":{
                "C->S":[
                    {
                        "id": 1,
                        "manufacturer": true,
                        "manufacturer_code": 1234
                    }
                ],
                "S->C":[
                    {
                        "id": 1,
                        "manufacturer": false
                    }
                ]
            }
        }
    :return:
    """
    data = ""
    data = data + to_hex(payload['endpoint_id'])
    data = data + big_small_end_convert_from_int(payload['cluster_id'])
    data = data + big_small_end_convert_from_int(payload['manufacturer_code'])
    data = data + to_hex(int(payload['server']))
    data = data + to_hex(len(payload['commands']['C->S']) + len(payload['commands']['S->C']))
    for command in payload['commands']['C->S']:
        data = data + to_hex(command['id'])
        data = data + to_hex(0)
        if command['manufacturer']:
            data = data + big_small_end_convert_from_int(payload['manufacturer_code'])
        else:
            data = data + "0000"
    for command in payload['commands']['S->C']:
        data = data + to_hex(command['id'])
        data = data + to_hex(1)
        if command['manufacturer']:
            data = data + big_small_end_convert_from_int(payload['manufacturer_code'])
        else:
            data = data + "0000"
    return encode(seq, zigbee_config_command + add_supported_command_to_cluster, data)


def supported_commands_list_request_handle(seq, payload=None):
    logger.info("function:%s, seq:%d", sys._getframe().f_code.co_name, seq)
    """

    :param payload:
        {
            "endpoint_id": 1,
            "cluster_id": 1234,
            'manufacturer": true,
            "manufacturer_code": 1234,
            "server": True
        }
    :return:
    """
    data = ""
    data = data + to_hex(payload['endpoint_id'])
    data = data + big_small_end_convert_from_int(payload['cluster_id'])
    if bool(payload['manufacturer']):
        data = data + big_small_end_convert_from_int(payload['manufacturer_code'])
    else:
        data = data + "0000"
    data = data + to_hex(int(payload['server']))

    return encode(seq, zigbee_config_command + supported_commands_list_request, data)


@response.cmd(zigbee_config_command + supported_commands_list_response, serial_protocol_schema_0211)
def supported_commands_list_response_handle(sequence, dongle, protocol):

    commands = {'C->S': [], 'S->C': []}
    for command in protocol.commands:
        _command = command.__dict__
        if command.manufacturer_code == 0:
            _command['manufacturer'] = False
            del _command['manufacturer_code']
        else:
            _command['manufacturer'] = True
        mask = command.mask
        del _command['mask']
        if mask == 'S->C':
            commands['S->C'].append(_command)
        else:
            commands['C->S'].append(_command)
    dongle.response(sequence, payload=commands)

import sys
from binascii import unhexlify

from zigbeeLauncher.serial_protocol import response
from zigbeeLauncher.serial_protocol.SerialProtocol import encode, big_small_end_convert, to_hex, \
    big_small_end_convert_to_int, big_small_end_convert_from_int, ack
from zigbeeLauncher.logging import dongleLogger as logger
from zigbeeLauncher.zigbee.DataType import get_bytes, data_type_value_table, data_type_name_table, data_type_table

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


@response.cmd(zigbee_config_command + node_info_response)
def node_info_response_handle(sequence, dongle, payload):
    logger.info("function:%s, seq:%d", sys._getframe().f_code.co_name, sequence)
    """

    :param data:
        byte0: zigbee device type
        byte1: radio power
        byte2-3: manufacturer code
    :return:
    """
    index = 0
    node = {"device_type": 'unknown'}
    for type in device_type:
        if device_type[type] == payload[index: index+2]:
            node["device_type"] = type
    index = index + 2
    node["radio_power"] = int(payload[index: index + 2], 16)
    index = index + 2
    node["manufacturer_code"] = big_small_end_convert_to_int(payload[index:index + 4])
    rsp = {'node': node}
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


@response.cmd(zigbee_config_command + endpoint_list_response)
def endpoint_list_response_handle(sequence, dongle, payload):
    logger.info("function:%s, seq:%d", sys._getframe().f_code.co_name, sequence)
    """
    byte0: number of endpoints
    """
    i = 0
    index = 0
    endpoints = {"endpoints": []}
    count = int(payload[index:index+2], 16)
    index = index + 2
    while i < count:
        endpoints['endpoints'].append({'id': int(payload[index+i*2:index+i*2+2], 16)})
        i = i + 1
    dongle.response(sequence, payload=endpoints)


def endpoint_descriptor_request_handle(seq, payload):
    logger.info("function:%s, seq:%d", sys._getframe().f_code.co_name, seq)
    endpoint = to_hex(payload)
    return encode(seq, zigbee_config_command + endpoint_descriptor_request, endpoint)


@response.cmd(zigbee_config_command + endpoint_descriptor_response)
def endpoint_descriptor_response_handle(sequence, dongle, payload):
    logger.info("function:%s, seq:%d", sys._getframe().f_code.co_name, sequence)
    """
    byte0: endpoint id
    byte1,2: profile id
    byte3,4: device id
    byte5: device version
    byte6: number of server clusters
    byte7: number of client clusters
    ...
    """
    index = 0
    id = int(payload[index:index + 2], 16)
    index = index + 2
    endpoint = {'id': id}
    endpoint["profile_id"] = big_small_end_convert_to_int(payload[index:index + 4])
    index = index + 4
    endpoint["device_id"] = big_small_end_convert_to_int(payload[index:index + 4])
    index = index + 4
    endpoint['device_version'] = int(payload[index: index + 2], 16)
    index = index + 2
    server_clusters = int(payload[index: index + 2], 16)
    index = index + 2
    client_clusters = int(payload[index: index + 2], 16)
    index = index + 2
    i = 0
    endpoint['server_clusters'] = []
    while i < server_clusters:
        cluster = {}
        i = i + 1
        cluster['id'] = big_small_end_convert_to_int(payload[index:index + 4])
        index = index + 4
        manufacturer_code = big_small_end_convert_to_int(payload[index:index + 4])
        index = index + 4
        if manufacturer_code == 0:
            cluster['manufacturer'] = False
        else:
            cluster['manufacturer'] = True
            cluster['manufacturer_code'] = manufacturer_code
        cluster['attributes'] = []
        cluster['commands'] = {'C->S':[], 'S->C': []}
        endpoint['server_clusters'].append(cluster)
    i = 0
    endpoint['client_clusters'] = []
    while i < client_clusters:
        cluster = {}
        i = i + 1
        cluster['id'] = big_small_end_convert_to_int(payload[index:index + 4])
        index = index + 4
        manufacturer_code = big_small_end_convert_to_int(payload[index:index + 4])
        index = index + 4
        if manufacturer_code == 0:
            cluster['manufacturer'] = False
        else:
            cluster['manufacturer'] = True
            cluster['manufacturer_code'] = manufacturer_code
        cluster['attributes'] = []
        cluster['commands'] = {'C->S':[], 'S->C': []}
        endpoint['client_clusters'].append(cluster)
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
            tmp = tmp + "".join(format(ord(c), "02X") for c in attribute['default'])
            if len(attribute['default']) < length:
                for i in range(0, length-len(attribute['default'])):
                    tmp = tmp + '00'
        else:
            length = get_bytes(type)
            tmp = tmp + to_hex(length)
            tmp = tmp + big_small_end_convert_from_int(attribute['default'], length)
        if len(head) + 2 + len(data) + len(tmp) > 400:
            # 将该attribute放到下一个包
            config.count = count+1
            data = head + to_hex(count) + data
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
    data = ""
    data = data + to_hex(payload['endpoint_id'])
    data = data + big_small_end_convert_from_int(payload['cluster_id'])
    if payload['manufacturer']:
        data = data + big_small_end_convert_from_int(payload['manufacturer_code'])
    else:
        data = data + "0000"
    data = data + to_hex(int(payload['server']))

    return encode(seq, zigbee_config_command + attribute_list_request, data)


@response.cmd(zigbee_config_command + attribute_list_response)
def attribute_list_response_handle(sequence, dongle, payload):
    logger.info("function:%s, seq:%d", sys._getframe().f_code.co_name, sequence)
    # ACK
    dongle.write(ack(zigbee_config_command + attribute_list_response, sequence))
    """

    :param data:
    byte0: endpoint id
    byte1-2: cluster id
    byte3-4: manufacturer code for cluster
    byte5: server/client
    byte6: total number of attributes
    byte7: remain number of attributes
    byte8: number of attributes
    byte9-10: attribute id
    byte11-12: manufacturer code
    byte13: type
    byte14: mask
    byte15: max length
    byte16-: value
    :return:
    """
    index = 0
    endpoint_id = int(payload[index:index + 2], 16)
    index = index + 2
    cluster_id = big_small_end_convert_to_int(payload[index:index + 4])
    index = index + 4
    manufacturer_code = big_small_end_convert_to_int(payload[index:index + 4])
    index = index + 4
    if manufacturer_code == 0:
        manufacturer = False
    else:
        manufacturer = True
    server = bool(int(payload[index:index+2], 16))
    index = index + 2
    total = int(payload[index:index+2], 16)
    index = index + 2
    remains = int(payload[index:index+2], 16)
    index = index + 2
    count = int(payload[index:index+2], 16)
    index = index + 2
    i = 0
    attributes = []
    while i < count:
        i = i + 1
        attribute = {"id": big_small_end_convert_to_int(payload[index:index + 4])}
        index = index + 4
        manufacturer_code = big_small_end_convert_to_int(payload[index:index + 4])
        index = index + 4
        if manufacturer_code == 0:
            attribute['manufacturer'] = False
        else:
            attribute['manufacturer'] = True
            attribute['manufacturer_code'] = manufacturer_code
        type = int(payload[index: index + 2], 16)
        index = index + 2
        if type in data_type_name_table:
            attribute['type'] = data_type_name_table[type]
        else:
            attribute['type'] = 'unknown'
        mask = int(payload[index: index+ 2], 16)
        index = index + 2
        attribute['writable'] = False
        if mask & 0x01:
            attribute['writable'] = True
        length = int(payload[index: index + 2], 16)
        index = index + 2
        # 设置value
        if 0x28 <= type <= 0x2F:
            # 有符号数
            # TODO: 将有符号数转换成对应的正数或者负数
            pass
        elif 0x41 <= type <= 0x51:
            # 字符串类型
            value = unhexlify(payload[index: index + length*2].encode('utf-8')).decode('utf-8')
            value = value[:value.find('\u0000')]
            attribute['length'] = length
            pass
        else:
            # 无符号数
            value = big_small_end_convert_to_int(payload[index: index+length*2])
        index = index + length * 2
        attribute['default'] = value
        attributes.append(attribute)
    if sequence == dongle.config.seq:
        return
    if endpoint_id != dongle.config.endpoint_id:
        return
    if cluster_id != dongle.config.cluster_id:
        return
    if server != dongle.config.server:
        return
    if manufacturer != dongle.config.manufacturer:
        return
    if manufacturer and manufacturer_code != dongle.config.manufacturer_code:
        return
    dongle.config.seq = sequence

    dongle.config.cluster['attributes'].extend(attributes)
    if remains == 0:
        dongle.config.next = True
    # rsp = {'response': endpoint}
    # if (seq, dongle.name) in commands:
    #     commands[(seq, dongle.name)].get_response(rsp)


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


@response.cmd(zigbee_config_command + attribute_response)
def attribute_response_handle(sequence, dongle, payload):
    logger.info("function:%s, seq:%d", sys._getframe().f_code.co_name, sequence)
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
    index = 0
    attribute = {'endpoint': int(payload[index:index + 2], 16)}
    index = index + 2
    attribute['cluster'] = big_small_end_convert_to_int(payload[index:index + 4])
    index = index + 4
    attribute['server'] = bool(int(payload[index:index + 2], 16))
    index = index + 2
    attribute['attribute'] = big_small_end_convert_to_int(payload[index:index + 4])
    index = index + 4
    manufacturer_code = big_small_end_convert_to_int(payload[index:index + 4])
    index = index + 4
    if manufacturer_code == 0:
        attribute['manufacturer'] = False
    else:
        attribute['manufacturer'] = True
    attribute['manufacturer_code'] = manufacturer_code
    attribute_property = payload[index:index + 2]
    index = index + 2
    type = int(payload[index:index + 2], 16)
    index = index + 2
    attribute['type'] = data_type_name_table[type]
    if get_bytes(type) == 0:
        # string type
        attribute['value'] = unhexlify(payload[index:].encode('utf-8')).decode('utf-8')
    else:
        attribute['value'] = big_small_end_convert_to_int(payload[index:])
    # update = {'attribute': attribute}
    rsp = {'response': attribute}
    # if (seq, dongle.name) in commands:
    #     commands[(seq, dongle.name)].get_response(rsp)
    # # need report this attribute if dongle ready
    # callback = get_value("dongle_update_callback")
    # if callback and dongle.ready:
    #     callback(dongle.name, update)
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
            "value": "this is a string"
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
    if length == 0:
        data = data + "".join(format(ord(c), "02X") for c in payload['value'])
    else:
        value = payload['value']
        if value < 0:
            # TODO: 将负数转换
            value = abs(~abs(value)) + 1
        data = data + big_small_end_convert_from_int(payload['value'], length)
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


@response.cmd(zigbee_config_command + supported_commands_list_response)
def supported_commands_list_response_handle(sequence, dongle, payload):
    logger.info("function:%s, seq:%d", sys._getframe().f_code.co_name, sequence)
    """

    :param data:
    byte0: endpoint id
    byte1-2: cluster id
    byte3-4: manufacturer id
    byte5: server/client
    byte6: number of commands
    byte7: command id
    byte8: command mask
    :return:
    """
    endpoint = {}
    index = 0
    id = int(payload[index:index + 2], 16)
    index = index + 2
    # TODO: 从config类中获取config并对比endpoint是否存在
    id = big_small_end_convert_to_int(payload[index:index + 4])
    index = index + 4
    manufacturer_code = big_small_end_convert_to_int(payload[index:index + 4])
    index = index + 4
    server = bool(int(payload[index:index + 2], 16))
    index = index + 2
    # TODO: 判断config数据中cluster是否存在
    total = int(payload[index:index + 2], 16)
    index = index + 2
    remains = int(payload[index:index + 2], 16)
    index = index + 2
    count = int(payload[index:index + 2], 16)
    index = index + 2
    i = 0
    _commands = {'C->S': [], 'S->C': []}
    while i < count:
        command = {}
        i = i + 1
        id = int(payload[index:index + 2], 16)
        index = index + 2
        mask = int(payload[index:index + 2], 16)
        index = index + 2
        manufacturer_code = big_small_end_convert_to_int(payload[index:index + 4])
        index = index + 4
        command['id'] = id
        if manufacturer_code == 0:
            command['manufacturer'] = False
        else:
            command['manufacturer'] = True
            command['manufacturer_code'] = manufacturer_code
        if mask & 0x01:
            # server to client
            _commands['S->C'].append(command)
        else:
            # client to server
            _commands['C->S'].append(command)

    dongle.response(sequence, payload=_commands)

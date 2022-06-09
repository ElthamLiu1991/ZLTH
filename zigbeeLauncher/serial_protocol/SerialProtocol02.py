from binascii import unhexlify

from zigbeeLauncher.mqtt.WiserZigbeeDongleCommands import commands
from zigbeeLauncher.serial_protocol.SerialProtocol import encode, big_small_end_convert, to_hex, \
    big_small_end_convert_to_int, big_small_end_convert_from_int
from zigbeeLauncher.mqtt import response, get_value
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


def node_info_write_handle(payload=None):
    """
    :param payload:
        {
            "device_type":'router',
            "radio_power": 10,
            "manufacturer_code": 1234
        }
    :return:
    """
    logger.debug("%s, payload:%s", __name__, str(payload))
    data = ""
    type = payload['device_type']
    if type in device_type:
        data = data + device_type[type]
    else:
        data = data + 'FF'
    data = data + to_hex(payload['radio_power'])
    data = data + big_small_end_convert(payload['manufacturer_code'])
    return encode(zigbee_config_command + node_info_write, data)


def node_info_request_handle(payload=None):
    logger.debug("%s, payload:%s", __name__, str(payload))
    return encode(zigbee_config_command + node_info_request, None)


@response.cmd(zigbee_config_command + node_info_response)
def node_info_response_handle(data):
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
        if device_type[type] == data.payload[index: index+2]:
            node["device_type"] = type
    index = index + 2
    node["radio_power"] = int(data.payload[index: index + 2], 16)
    index = index + 2
    node["manufacturer_code"] = big_small_end_convert_to_int(data.payload[index:index + 4])
    rsp = {'node': node}
    # TODO: send rsp to config class


def add_endpoint_handle(payload=None):
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
                    "manufacturer_code": 1234
                }
            ],
            "client_clusters":[
                {
                    "id": 1234,
                    "manufacturer_code": 1234
                }
            ]
        }
    :return:
    """
    logger.debug("%s, payload:%s", __name__, str(payload))
    data = ""
    data = data + to_hex(payload['id'])
    data = data + big_small_end_convert(payload['profile_id'])
    data = data + big_small_end_convert(payload['device_id'])
    data = data + big_small_end_convert(payload['device_version'])
    data = data + to_hex(len(payload['server_clusters']))
    data = data + to_hex(len(payload['client_clusters']))
    for cluster in payload['server_clusters']:
        data = data + big_small_end_convert(cluster['id'])
        data = data + big_small_end_convert(cluster['manufacturer_code'])
    for cluster in payload['client_clusters']:
        data = data + big_small_end_convert(cluster['id'])
        data = data + big_small_end_convert(cluster['manufacturer_code'])
    return encode(zigbee_config_command + add_endpoint, data)


def endpoint_list_request_handle(payload=None):
    logger.debug("%s, payload:%s", __name__, str(payload))
    return encode(zigbee_config_command + endpoint_list_request, None)


@response.cmd(zigbee_config_command + endpoint_list_response)
def endpoint_list_response_handle(data):
    """
    byte0: number of endpoints
    """
    i = 0
    rsp = {"endpoints": []}
    endpoints = int(data.payload[:2], 16)
    while i < endpoints:
        i = i + 1
        rsp['endpoints'].append(data.payload[2 * i:2 * (1 + i)])
    if (data.seq, data.dongle.name) in commands:
        commands[(data.seq, data.dongle.name)].get_response(rsp)
    pass


def endpoint_descriptor_request_handle(payload):
    logger.debug("%s, payload:%s", __name__, str(payload))
    return encode(zigbee_config_command + endpoint_descriptor_request, payload)


@response.cmd(zigbee_config_command + endpoint_descriptor_response)
def endpoint_descriptor_response_handle(data):
    """
    byte0: endpoint id
    byte1,2: profile id
    byte3,4: device id
    byte5: device version
    byte6: number of server clusters
    byte7: number of client clusters
    ...
    """
    """
    处理逻辑：
    1. 从config类中取出当前设备的config数据
        a. 如果没有数据，则退出
        b. 如果有则继续
    2. 从config数据中查找是否有对应的endpoint值
        a. 如果没有，则退出
        b. 如果有则继续
    3. 打包该endpoint的数据
    4. cluster不需要提供'name'属性
        
    """
    config = {}
    index = 0
    id = int(data.payload[index:index + 2], 16)
    index = index + 2
    # TODO: 从config类中获取config并对比endpoint是否存在

    endpoint = {"profile_id": big_small_end_convert_to_int(data.payload[index:index + 4])}
    index = index + 4
    endpoint["device_id"] = big_small_end_convert_to_int(data.payload[index:index + 4])
    index = index + 4
    endpoint['device_version'] = int(data.payload[index: index + 2], 16)
    index = index + 2
    server_clusters = int(data.payload[index: index + 2], 16)
    index = index + 2
    client_clusters = int(data.payload[index: index + 2], 16)
    index = index + 2
    i = 0
    endpoint['server_clusters'] = []
    while i < server_clusters:
        cluster = {}
        i = i + 1
        cluster['id'] = big_small_end_convert_to_int(data.payload[index:index + 4])
        index = index + 4
        manufacturer_code = big_small_end_convert_to_int(data.payload[index:index + 4])
        cluster['manufacturer_code'] = manufacturer_code
        index = index + 4
        if manufacturer_code == 0:
            cluster['manufacturer'] = False
        else:
            cluster['manufacturer'] = True
        cluster['attributes'] = []
        cluster['commands'] = []
        endpoint['server_clusters'].append(cluster)
    i = 0
    endpoint['client_clusters'] = []
    while i < client_clusters:
        cluster = {}
        i = i + 1
        cluster['id'] = big_small_end_convert_to_int(data.payload[index:index + 4])
        index = index + 4
        manufacturer_code = big_small_end_convert_to_int(data.payload[index:index + 4])
        cluster['manufacturer_code'] = manufacturer_code
        index = index + 4
        if manufacturer_code == "0000":
            cluster['manufacturer'] = False
        else:
            cluster['manufacturer'] = True
        cluster['attributes'] = []
        cluster['commands'] = []
        endpoint['client_clusters'].append(cluster)
    # TODO: 将endpoint数据加入到config数据
    if (data.seq, data.dongle.name) in commands:
        commands[(data.seq, data.dongle.name)].get_response(config)
    pass


def add_attributes_to_cluster_handle(payload=None):
    """

    :param payload:
        {
            "endpoint_id": 1,
            "cluster_id": 1234,
            "manufacturer_code":1234,
            "server": True,
            "attributes":[
                {
                    "id": 1234,
                    "manufacturer_code": 1234,
                    "type":"uint16",
                    "length": 1
                    "writable": False
                }
            ]
        }
    :return:
    """
    logger.debug("%s, payload:%s", __name__, str(payload))
    data = ""
    data = data + to_hex(payload['endpoint_id'])
    data = data + big_small_end_convert(payload['cluster_id'])
    data = data + big_small_end_convert(payload['manufacturer_code'])
    data = data + to_hex(int(payload['server']))
    data = data + to_hex(len(payload['attributes']))
    for attribute in payload['attributes']:
        data = data + big_small_end_convert(attribute['id'])
        data = data + big_small_end_convert(attribute['manufacturer_code'])
        type = attribute['type']
        if type in data_type_value_table:
            data = data + to_hex(data_type_value_table[attribute['type']])
        else:
            data = data + 'FF'
        mask = 2
        if attribute['writable']:
            mask = mask + 1
        data = data + to_hex(mask)
        data = data + to_hex(attribute['length'])
    return encode(zigbee_config_command + add_attributes_to_cluster, data)


def attribute_list_request_handle(payload=None):
    """

    :param payload:
        {
            "endpoint_id": 1,
            "cluster_id": 1234,
            "manufacturer_code": 1234,
            "server": False
        }
    :return:
    """
    logger.debug("%s, payload:%s", __name__, str(payload))
    data = ""
    data = data + to_hex(payload['endpoint_id'])
    data = data + big_small_end_convert(payload['cluster_id'])
    data = data + big_small_end_convert(payload['manufacturer_code'])
    data = data + to_hex(int(payload['server']))

    return encode(zigbee_config_command + attribute_list_request, data)


@response.cmd(zigbee_config_command + attribute_list_response)
def attribute_list_response_handle(data):
    """

    :param data:
    byte0: endpoint id
    byte1-2: cluster id
    byte3-4: manufacturer code
    byte5: server/client
    byte6: number of page
    byte7: current page
    byte8: number of attributes
    byte9-10: attribute id
    byte11-12: manufacturer code
    byte13: type
    byte14: mask
    byte15: length
    :return:
    """
    """
        处理逻辑：
        1. 从config类中取出当前设备的config数据
            a. 如果没有数据，则退出
            b. 如果有则继续
        2. 从config数据中查找是否有对应的endpoint值
            a. 如果没有，则退出
            b. 如果有则继续
        3. 从endpoint数据中查找是否有对应的cluster值
            a. 如果没有，则退出
            b. 如果有则继续
        4. attribute不需要提供'name'属性
            

    """
    config = {}
    index = 0
    id = int(data.payload[index:index + 2], 16)
    index = index + 2
    # TODO: 从config类中获取config并对比endpoint是否存在
    id = big_small_end_convert_to_int(data.payload[index:index + 4])
    index = index + 4
    manufacturer_code = big_small_end_convert_to_int(data.payload[index:index + 4])
    index = index + 4
    server = bool(int(data.payload[index:index+2]))
    index = index + 2
    # TODO: 判断config数据中cluster是否存在
    total_pages = int(data.payload[index:index+2])
    index = index + 2
    current_page = int(data.payload[index:index+2])
    index = index + 2
    count = int(data.payload[index:index+2])
    index = index + 2
    i = 0
    attributes = []
    while i < count:
        attribute = {"id": big_small_end_convert_to_int(data.payload[index:index + 4])}
        index = index + 4
        attribute["manufacturer_code"] = big_small_end_convert_to_int(data.payload[index:index + 4])
        index = index + 4
        if attribute['manufacturer_code'] == 0:
            attribute['manufacturer'] = False
        else:
            attribute['manufacturer'] = True
            type = int(data.payload[index: index + 2], 16)
            index = index + 2
            if type in data_type_name_table:
                attribute['type'] = data_type_name_table[type]
            else:
                attribute['type'] = 'unknown'
            mask = int(data.payload[index: index+ 2], 16)
            index = index + 2
            attribute['writable'] = False
            attribute['reportable'] = False
            if mask & 0x01:
                attribute['writable'] = True
            if mask & 0x02:
                attribute['reportable'] = True
            attribute['length'] = int(data.payload[index: index + 2], 16)
            index = index + 2
            attributes.append(attribute)
    # TODO: 将attributes数据加入cluster
    if (data.seq, data.dongle.name) in commands:
        commands[(data.seq, data.dongle.name)].get_response(config)
    pass


def attribute_request_handle(payload):
    logger.debug("%s, payload:%s", __name__, str(payload))

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
    return encode(zigbee_config_command + attribute_request, data)


@response.cmd(zigbee_config_command + attribute_response)
def attribute_response_handle(data):
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
    attribute = {'endpoint': int(data.payload[index:index + 2], 16)}
    index = index + 2
    attribute['cluster'] = big_small_end_convert_to_int(data.payload[index:index + 4])
    index = index + 4
    attribute['server'] = bool(int(data.payload[index:index + 2], 16))
    index = index + 2
    attribute['attribute'] = big_small_end_convert_to_int(data.payload[index:index + 4])
    index = index + 4
    manufacturer_code = big_small_end_convert_to_int(data.payload[index:index + 4])
    index = index + 4
    if manufacturer_code == 0:
        attribute['manufacturer'] = False
    else:
        attribute['manufacturer'] = True
    attribute['manufacturer_code'] = manufacturer_code
    attribute_property = data.payload[index:index + 2]
    index = index + 2
    type = int(data.payload[index:index + 2], 16)
    index = index + 2
    attribute['type'] = data_type_name_table[type]
    if get_bytes(type) == 0:
        # string type
        attribute['value'] = unhexlify(data.payload[index:].encode('utf-8')).decode('utf-8')
    else:
        attribute['value'] = big_small_end_convert_to_int(data.payload[index:])
    update = {'attribute': attribute}
    rsp = {'response': attribute}
    if (data.seq, data.dongle.name) in commands:
        commands[(data.seq, data.dongle.name)].get_response(rsp)
    # need report this attribute if dongle ready
    callback = get_value("dongle_update_callback")
    if callback and data.dongle.ready:
        callback(data.dongle.name, update)


def attribute_write_request_handle(payload):
    logger.debug("%s, payload:%s", __name__, str(payload))
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
        data = data + big_small_end_convert_from_int(payload['value'], length)
    print('data:', data)
    return encode(zigbee_config_command + attribute_write_request, data)


def attribute_default_value_write_handle(payload=None):
    logger.debug("%s, payload:%s", __name__, str(payload))
    return encode(zigbee_config_command + attribute_default_value_write, None)


def add_supported_command_to_cluster_handle(payload=None):
    """

    :param payload:
        {
            "endpoint_id": 1,
            "cluster_id": 1234,
            "manufacturer_code": 1234,
            "server": True,
            "commands":[
                {
                    "generated":[
                        {
                            "id": 1,
                            "manufacturer_code": 1234
                        }
                    ],
                    "received":[
                        {
                            "id": 1,
                            "manufacturer_code": 1234
                        }
                    ]
                }
            ]
        }
    :return:
    """
    logger.debug("%s, payload:%s", __name__, str(payload))
    return encode(zigbee_config_command + add_supported_command_to_cluster, None)


def supported_commands_list_request_handle(payload=None):
    """

    :param payload:
        {
            "endpoint_id": 1,
            "cluster_id": 1234,
            "manufacturer_code": 1234,
            "server": True
        }
    :return:
    """
    logger.debug("%s, payload:%s", __name__, str(payload))
    data = ""
    data = data + to_hex(payload['endpoint_id'])
    data = data + big_small_end_convert(payload['cluster_id'])
    data = data + big_small_end_convert(payload['manufacturer_code'])
    data = data + to_hex(int(payload['server']))

    return encode(zigbee_config_command + supported_commands_list_request, data)


@response.cmd(zigbee_config_command + supported_commands_list_response)
def supported_commands_list_response_handle(data):
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
    """
        处理逻辑：
        1. 从config类中取出当前设备的config数据
            a. 如果没有数据，则退出
            b. 如果有则继续
        2. 从config数据中查找是否有对应的endpoint值
            a. 如果没有，则退出
            b. 如果有则继续
        3. 从endpoint数据中查找是否有对应的cluster值
            a. 如果没有，则退出
            b. 如果有则继续
        4. command不需要提供description
    """
    config = {}
    index = 0
    id = int(data.payload[index:index + 2], 16)
    index = index + 2
    # TODO: 从config类中获取config并对比endpoint是否存在
    id = big_small_end_convert_to_int(data.payload[index:index + 4])
    index = index + 4
    manufacturer_code = big_small_end_convert_to_int(data.payload[index:index + 4])
    index = index + 4
    server = bool(int(data.payload[index:index + 2]))
    index = index + 2
    # TODO: 判断config数据中cluster是否存在
    count = int(data.payload[index:index + 2])
    index = index + 2
    i =0
    commands = {'generated':[], 'received':[]}
    while i < count:
        id = int(data.payload[index:index + 2])
        index = index + 2
        mask = int(data.payload[index:index + 2])
        index = index + 2
        if mask & 0x01:
            # server to client
            commands['generated'].append({'id': id})
        else:
            # client to server
            commands['received'].append({'id': id})
    # TODO: 将commands数据加入cluster
    if (data.seq, data.dongle.name) in commands:
        commands[(data.seq, data.dongle.name)].get_response(config)
    pass
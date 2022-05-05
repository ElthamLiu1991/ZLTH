from binascii import unhexlify

from zigbeeLauncher.mqtt.WiserZigbeeDongleCommands import commands
from zigbeeLauncher.serial_protocol.SerialProtocol import encode, big_small_end_convert, to_hex
from zigbeeLauncher.mqtt import response, get_value
from zigbeeLauncher.logging import dongleLogger as logger
from zigbeeLauncher.zigbee.DataType import get_bytes

zigbee_config_command = "02"
endpoint_list_request = "04"
endpoint_list_response = "05"
endpoint_descriptor_request = '06'
endpoint_descriptor_response = '07'
attribute_request = '0B'
attribute_response = '0C'
attribute_write_request = '0D'


def endpoint_list_request_handle(payload=None):
    return encode(zigbee_config_command + endpoint_list_request, None)


@response.cmd(zigbee_config_command + endpoint_list_response)
def endpoint_list_response_handle(data):
    """
    byte0: number of endpoints
    """
    i = 0
    rsp = {"endpoint": []}
    endpoints = int(data.payload[:2], 16)
    while i < endpoints:
        i = i + 1
        rsp['endpoint'].append(data.payload[2 * i:2 * (1 + i)])
    if (data.seq, data.dongle.name) in commands:
        commands[(data.seq, data.dongle.name)].get_response(rsp)
    pass


def endpoint_descriptor_request_handle(payload):
    return encode(zigbee_config_command + endpoint_descriptor_request, payload)


@response.cmd(zigbee_config_command + endpoint_descriptor_response)
def endpoint_descriptor_response_handle(data):
    """
    byte0: endpoint id
    byte1,2: profile id
    byte3,4: device id
    byte5: device version
    byte6: number of server cluster
    """
    index = 0
    rsp = {}
    endpoint = {}
    endpoint.update({"endpoint": int(data.payload[index:index + 2], 16)})
    index = index + 2
    endpoint.update({"profile": big_small_end_convert(data.payload[index:index + 4])})
    index = index + 4
    endpoint.update({"device_id": big_small_end_convert(data.payload[index:index + 4])})
    index = index + 4
    endpoint.update({"device_version": int(data.payload[index: index + 2], 16)})
    index = index + 2
    server_clusters = int(data.payload[index: index + 2], 16)
    index = index + 2
    client_clusters = int(data.payload[index: index + 2], 16)
    index = index + 2
    i = 0
    endpoint['server_clusters'] = []
    while i < server_clusters:
        i = i + 1
        cluster = big_small_end_convert(data.payload[index:index + 4])
        index = index + 4
        manufacturer_code = big_small_end_convert(data.payload[index:index + 4])
        index = index + 4
        if manufacturer_code == "0000":
            manufacturer = False
        else:
            manufacturer = True
        attributes = []
        if cluster == '0006':
            attributes.append({'attribute': '0000', 'name': 'onoff', 'type': '10', 'value': "0"})
        if cluster == '0402':
            attributes.append({'attribute': '0000', 'name': 'temperature', 'type': '29', 'value': "0"})
        if cluster == '0405':
            attributes.append({'attribute': '0000', 'name': 'humidity', 'type': '21', 'value': "0"})
        # TODO: get cluster name
        endpoint['server_clusters'].append({'cluster': cluster, 'name': cluster, 'manufacturer': manufacturer,
                                            'manufacturer_code': manufacturer_code, 'attributes': attributes})
    i = 0
    endpoint['client_clusters'] = []
    while i < client_clusters:
        i = i + 1
        cluster = big_small_end_convert(data.payload[index:index + 4])
        index = index + 4
        manufacturer_code = big_small_end_convert(data.payload[index:index + 4])
        index = index + 4
        if manufacturer_code == "0000":
            manufacturer = False
        else:
            manufacturer = True
        attributes = []
        # TODO: get cluster name
        endpoint['client_clusters'].append({'cluster': cluster, 'name': cluster, 'manufacturer': manufacturer,
                                            'manufacturer_code': manufacturer_code, 'attributes': attributes})
    rsp['descriptor'] = endpoint
    if (data.seq, data.dongle.name) in commands:
        commands[(data.seq, data.dongle.name)].get_response(rsp)
    pass


def attribute_request_handle(payload):
    """
        :param payload:
        {
            "endpoint":1,
            "cluster": "0006",
            "server":true,
            "attribute": "0000",
            "manufacturer":false,
            "manufacturer_code":"0000"
        }
        :return:
        """
    data = ""
    data = data + to_hex(payload['endpoint'])
    data = data + big_small_end_convert(payload['cluster'])
    data = data + to_hex(int(payload['server']))
    data = data + big_small_end_convert(payload['attribute'])
    data = data + big_small_end_convert(payload['manufacturer_code'])
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
    rsp = {}
    attribute = {'endpoint': int(data.payload[index:index + 2], 16)}
    index = index + 2
    attribute['cluster'] = big_small_end_convert(data.payload[index:index + 4])
    index = index + 4
    attribute['server'] = bool(int(data.payload[index:index + 2], 16))
    index = index + 2
    attribute['attribute'] = big_small_end_convert(data.payload[index:index + 4])
    index = index + 4
    manufacturer_code = big_small_end_convert(data.payload[index:index + 4])
    index = index + 4
    attribute_property = data.payload[index:index + 2]
    index = index + 2
    type = data.payload[index:index + 2]
    index = index + 2
    if get_bytes(type) == 0:
        # string type
        attribute['value'] = unhexlify(data.payload[index:].encode('utf-8')).decode('utf-8')
    else:
        attribute['value'] = str(int(big_small_end_convert(data.payload[index:]), 16))
    rsp['attribute'] = attribute
    if (data.seq, data.dongle.name) in commands:
        commands[(data.seq, data.dongle.name)].get_response(rsp)
    else:
        # update
        if get_value("dongle_update_callback"):
            get_value("dongle_update_callback")(data.dongle.name, rsp)


def attribute_write_request_handle(payload):
    """
        :param payload:
        {
            "endpoint":1,
            "cluster": "0006",
            "server":true,
            "attribute": "0000",
            "manufacturer":false,
            "manufacturer_code":"105E",
            "type": "10",
            "value": "00"
        }
        :return:
        """
    attribute = payload['attribute']
    data = ""
    data = data + to_hex(attribute['endpoint'])
    data = data + big_small_end_convert(attribute['cluster'])
    data = data + to_hex(int(attribute['server']))
    data = data + big_small_end_convert(attribute['attribute'])
    data = data + big_small_end_convert(attribute['manufacturer_code'])
    data = data + attribute['type']

    length = get_bytes(attribute['type'])
    if length == 0:
        data = data + "".join(format(ord(c), "02X") for c in attribute['value'])
    else:
        data = data + big_small_end_convert(hex(int(attribute['value']))[2:])
    # 删除payload里面的manufacturer_code和type
    del attribute['manufacturer_code']
    del attribute['type']
    print(payload)
    return encode(zigbee_config_command + attribute_write_request, data)

from zigbeeLauncher.serial_protocol import response
from zigbeeLauncher.serial_protocol.SerialProtocol import encode, big_small_end_convert, to_hex, \
    big_small_end_convert_from_int, big_small_end_convert_to_int

network_config_command = "01"
network_status_request = "00"
network_status_response = "01"
join_network_request = "02"
form_network_request = "03"
permit_join_request = "04"
leave_network_request = "05"
data_request = '09'


def network_status_request_handle(seq, payload=None):
    return encode(seq, network_config_command + network_status_request, None)


@response.cmd(network_config_command + network_status_response)
def network_status_response_handle(sequence, dongle, payload):
    """
    byte0: network state
    byte1: zigbee device type
    byte2: zigbee network channel
    byte3,4: zigbee network PAN ID
    byte5,6: zigbee network node ID
    byte7-14: zigbee network extended PAN ID
    """
    rsp = {}
    index = 0
    state = payload[index:index + 2]
    index = index + 2
    if state == "00":
        rsp.update({"state": 1})
    elif state == "01":
        rsp.update({"state": 6})
    elif state == "02":
        rsp.update({"state": 5})
    elif state == "10":
        rsp.update({"state": 7})
    elif state == "11":
        rsp.update({"state": 4})
    # dongle.property.state = rsp['state']
    dongle.property.update(**rsp)
    zigbee = {}
    device_type = payload[index:index + 2]
    index = index + 2
    if device_type == "00":
        zigbee.update({"device_type": "coordinator"})
    elif device_type == "01":
        zigbee.update({"device_type": "router"})
    elif device_type == "02":
        zigbee.update({"device_type": "end device"})
    elif device_type == "03":
        zigbee.update({"device_type": "sleepy end device"})
    elif device_type == "FF":
        zigbee.update({"device_type": "unknown"})
    channel = payload[index:index + 2]
    index = index + 2
    zigbee.update({"channel": int(channel, 16)})
    pan_id = payload[index:index + 4]
    index = index + 4
    zigbee.update({"pan_id": big_small_end_convert_to_int(pan_id)})
    node_id = payload[index:index + 4]
    index = index + 4
    zigbee.update({"node_id": big_small_end_convert_to_int(node_id)})
    extended_pan_id = payload[index:index + 16]
    index = index + 16
    zigbee.update({"extended_pan_id": big_small_end_convert_to_int(extended_pan_id)})
    rsp['zigbee'] = zigbee
    dongle.property.update(**rsp)
    # need report this attribute if dongle ready
    # update = get_value("dongle_update_callback")
    # if update and dongle.property.ready:
    #     update(dongle.property..mac, rsp)
    dongle.response(sequence, payload=rsp)


def join_network_request_handle(seq, payload):
    """

    :param payload:
    {
        "channel_mask": 0x7FFF800,
        "auto_option": 3,
        "pan_id": 0x12AB,
        "extended_pan_id":0x11223344AABBCCDD
    }
    :return:
    """
    data = ""
    data = data + big_small_end_convert_from_int(payload['channel_mask'], 4)
    data = data + to_hex(payload['auto_option'])
    data = data + big_small_end_convert_from_int(payload['pan_id'], 2)
    data = data + big_small_end_convert_from_int(payload['extended_pan_id'], 8)
    return encode(seq, network_config_command + join_network_request, data)


def form_network_request_handle(seq, payload):
    """
    :param payload:
    {
        "channel": 11,
        "auto_option": 3,
        "pan_id": "12AB",
        "extended_pan_id":"11223344AABBCCDD"
    }
    :return:
    """
    data = ""
    data = data + big_small_end_convert(hex(payload['channel'])[2:])
    data = data + to_hex(payload['auto_option'])
    data = data + payload['pan_id']
    data = data + payload['extended_pan_id']
    return encode(seq, network_config_command + form_network_request, data)


def permit_join_request_handle(seq, payload=None):
    data = to_hex(payload)
    return encode(seq, network_config_command + permit_join_request, data)


def leave_network_request_handle(seq):
    return encode(seq, network_config_command + leave_network_request, None)


def data_request_handle(seq):
    return encode(seq, network_config_command + data_request, None)

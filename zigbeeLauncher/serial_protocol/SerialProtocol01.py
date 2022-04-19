from zigbeeLauncher.mqtt.WiserZigbeeDongleCommands import commands
from zigbeeLauncher.serial_protocol.SerialProtocol import encode, big_small_end_convert, to_hex
from zigbeeLauncher.mqtt import response, get_value

network_config_command = "01"
network_status_request = "00"
network_status_response = "01"
join_network_request = "02"
form_network_request = "03"
permit_join_request = "04"
leave_network_request = "05"


def network_status_request_handle(payload=None):
    return encode(network_config_command + network_status_request, None)


@response.cmd(network_config_command + network_status_response)
def network_status_response_handle(data):
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
    state = data.payload[index:index + 2]
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
    data.dongle.set_attributes(state=rsp['state'])
    zigbee = {}
    device_type = data.payload[index:index + 2]
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
    channel = data.payload[index:index + 2]
    index = index + 2
    zigbee.update({"channel": int(channel, 16)})
    pan_id = data.payload[index:index + 4]
    index = index + 4
    zigbee.update({"pan_id": big_small_end_convert(pan_id)})
    node_id = data.payload[index:index + 4]
    index = index + 4
    zigbee.update({"node_id": big_small_end_convert(node_id)})
    extended_pan_id = data.payload[index:index + 16]
    index = index + 16
    zigbee.update({"extended_pan_id": big_small_end_convert(extended_pan_id)})
    rsp['zigbee'] = zigbee
    if (data.seq, data.dongle.name) in commands:
        commands[(data.seq, data.dongle.name)].get_response(rsp)
    else:
        # update
        if get_value("dongle_update_callback"):
            get_value("dongle_update_callback")(data.dongle.name, rsp)


def join_network_request_handle(payload):
    """

    :param payload:
    {
        "channel_mask": "7FFF800",
        "auto_option": 3,
        "pan_id": "12AB",
        "extended_pan_id":"11223344AABBCCDD"
    }
    :return:
    """
    data = ""
    data = data + big_small_end_convert(payload['channel_mask'])
    data = data + to_hex(payload['auto_option'])
    data = data + payload['pan_id']
    data = data + payload['extended_pan_id']
    return encode(network_config_command + join_network_request, data)


def form_network_request_handle(payload):
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
    return encode(network_config_command + form_network_request, data)


def permit_join_request_handle(payload):
    data = to_hex(payload)
    return encode(network_config_command + permit_join_request, data)


def leave_network_request_handle(payload=None):
    return encode(network_config_command + leave_network_request, payload)

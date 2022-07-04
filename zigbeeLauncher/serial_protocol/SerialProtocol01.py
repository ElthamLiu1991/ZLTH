from zigbeeLauncher.serial_protocol import response
from zigbeeLauncher.serial_protocol.SerialProtocol import encode, big_small_end_convert, to_hex, \
    big_small_end_convert_from_int, big_small_end_convert_to_int


serial_protocol_schema_0101 = {
                "state":{
                    "type": 'integer',
                    'length': 1,
                    'enumerate':{
                        0x00: 1,
                        0x01: 6,
                        0x02: 5,
                        0x10: 7,
                        0x11: 4
                    }
                },
                'device_type':{
                    'type': 'integer',
                    'length': 1,
                    'enumerate':{
                        0x00: 'coordinator',
                        0x01: 'router',
                        0x02: 'end_device',
                        0x03: 'sleepy_end_device',
                        0xFF: 'unknown'
                    }
                },
                'channel':{
                    'type': 'integer',
                    'length': 1
                },
                "pan_id":{
                    "type": 'integer',
                    'length': 2
                },
                'node_id':{
                    'type': 'integer',
                    'length': 2
                },
                'extended_pan_id':{
                    'type': 'integer',
                    'length': 8
                },
                'permit_join_time':{
                    'type': 'integer',
                    'length': 1
                }
            }


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


@response.cmd(network_config_command + network_status_response, serial_protocol_schema_0101)
def network_status_response_handle(sequence, dongle, protocol):
    """
    byte0: network state
    byte1: zigbee device type
    byte2: zigbee network channel
    byte3,4: zigbee network PAN ID
    byte5,6: zigbee network node ID
    byte7-14: zigbee network extended PAN ID
    """
    rsp = {}
    state = protocol.state
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
    dongle.property.update(state=protocol.state)

    zigbee = protocol.__dict__
    del zigbee['state']
    del zigbee['permit_join_time']

    rsp['zigbee'] = zigbee
    dongle.property.update(zigbee=zigbee)
    dongle.response(sequence, payload=rsp)


def join_network_request_handle(seq, payload):
    """

    :param payload:
    {
        "channels": [11,12],
        "pan_id": 0x12AB,
        "extended_pan_id":0x11223344AABBCCDD
    }
    :return:
    """
    data = ""
    channel_mask = 0
    for item in payload['channels']:
        channel_mask = channel_mask + (1 << item)
    data = data + big_small_end_convert_from_int(channel_mask, 4)
    auto_option = 0
    pan_id = 0
    extended_pan_id = 0
    if 'pan_id' in payload:
        auto_option = auto_option + 1
        pan_id = payload['pan_id']
    if 'extended_pan_id' in payload:
        auto_option = auto_option + 2
        extended_pan_id = payload['extended_pan_id']
    data = data + to_hex(auto_option)
    data = data + big_small_end_convert_from_int(pan_id, 2)
    data = data + big_small_end_convert_from_int(extended_pan_id, 8)
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

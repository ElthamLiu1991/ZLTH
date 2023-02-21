from dataclasses import asdict

from zigbeeLauncher.data_model import ZigbeeInfo
from zigbeeLauncher.serial_protocol.sp import SerialProtocol, Response, SPType


class GetZigbee(SerialProtocol):
    id = 0x0100

    def __init__(self):
        super().__init__(self.id)


@Response
class ZigbeeResponse(SerialProtocol):
    id = 0x0101

    def __setattr__(self, key, value):
        if value is not None:
            if key == 'state':
                if value == 0x00:
                    self.dongle.state = self.dongle.DongleState.UN_COMMISSIONED
                elif value == 0x01:
                    self.dongle.state = self.dongle.DongleState.JOINED
                elif value == 0x10:
                    self.dongle.state = self.dongle.DongleState.ORPHAN
                elif value == 0x11:
                    self.dongle.state = self.dongle.DongleState.PAIRING
            elif key == 'type':
                if value == 0xFF:
                    value = 'unknown'
                else:
                    value = ['coordinator', 'router', 'end_device', 'sleepy_end_device'][value]
            elif key == 'extended_pan':
                value = hex(value)[2:].upper()
            elif key == 'permit':
                # pack zigbee
                self.dongle.zigbee = asdict(ZigbeeInfo(
                    mac=self.dongle.mac,
                    device_type=self.type,
                    channel=self.channel,
                    node_id=self.node,
                    pan_id=self.pan,
                    extended_pan_id=self.extended_pan
                ))
                pass
        self.__dict__[key] = value

    def __init__(self):
        super().__init__(self.id)
        self.register('state', SPType.INT, 1)
        self.register('type', SPType.INT, 1)
        self.register('channel', SPType.INT, 1)
        self.register('pan', SPType.INT, 2)
        self.register('node', SPType.INT, 2)
        self.register('extended_pan', SPType.INT, 8)
        self.register('permit', SPType.INT, 1)


class JoinNetwork(SerialProtocol):
    id = 0x0102

    def __setattr__(self, key, value):
        if key == 'pan_id':
            if value is None:
                value = 0
                self.__dict__['auto'] = 0x01
            else:
                self.__dict__['auto'] = 0x00
        if key == 'extended_pan':
            if value is None:
                value = 0
                self.__dict__['auto'] |= 0x02
        self.__dict__[key] = value

    def __init__(self, channel=0, auto=0, pan_id=0, extended_pan=0):
        super().__init__(self.id)
        self.register('channel', SPType.INT, 4, channel)
        self.register('auto', SPType.INT, 1, auto)
        self.register('pan_id', SPType.INT, 2, pan_id)
        self.register('extended_pan', SPType.INT, 8, extended_pan)


class Leave(SerialProtocol):
    id = 0x0105

    def __init__(self):
        super().__init__(self.id)


class DataRequest(SerialProtocol):
    id = 0x0109

    def __init__(self):
        super().__init__(self.id)
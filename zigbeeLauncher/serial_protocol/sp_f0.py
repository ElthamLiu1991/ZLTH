from zigbeeLauncher.serial_protocol.sp import SerialProtocol, Response, SPType, ACK

BOOTLOADER_SEQ = 0x1000
UPGRADE_START_SEQ = 0x1001
UPGRADE_STOP_SEQ = 0x1002

RESET_SEQ = 0x80


class Reset(SerialProtocol):
    id = 0xF000

    def __init__(self):
        super().__init__(self.id)


class EnterBootloader(SerialProtocol):
    id = 0xF001

    def __init__(self):
        super().__init__(self.id)


class GetInfo(SerialProtocol):
    id = 0xF002

    def __init__(self):
        super().__init__(self.id)


@Response
class InfoResponse(SerialProtocol):
    id = 0xF003

    def __setattr__(self, key, value):
        if value is not None:
            if key == 'build_version':
                self.dongle.connected = True
                self.dongle.swversion = f'{self.major_version}.{self.minor_version}.{value}'
            elif key == 'hardware_version':
                self.dongle.hwversion = f'{value}'
        self.__dict__[key] = value

    def __init__(self):
        super().__init__(self.id)
        self.register('major_version', SPType.INT, 1)
        self.register('minor_version', SPType.INT, 1)
        self.register('build_version', SPType.INT, 1)
        self.register('application_information', SPType.INT, 1)
        self.register('eui', SPType.INT, 8)
        self.register('hardware_version', SPType.INT, 1)
        self.register('bootloader_type', SPType.INT, 1)


class GetLabel(SerialProtocol):
    id = 0xF004

    def __init__(self):
        super().__init__(self.id)


@Response
class LabelResponse(SerialProtocol):
    id = 0xF005

    def __setattr__(self, key, value):
        print(key, value)
        if value is not None:
            if key == 'label':
                self.dongle.label = value
        self.__dict__[key] = value

    def __init__(self):
        super().__init__(self.id)
        self.register('len', SPType.INT, 1)
        self.register('label', SPType.STR, 0)


class WriteLabel(SerialProtocol):
    id = 0xF006

    def __init__(self, label=''):
        super().__init__(self.id)
        self.register('len', SPType.INT, 1, len(label))
        self.register('label', SPType.STR, len(label) + 1, label)


class Identify(SerialProtocol):
    id = 0xF007

    def __init__(self):
        super().__init__(self.id)


class GetState(SerialProtocol):
    id = 0xF008

    def __init__(self):
        super().__init__(self.id)


@Response
class StateResponse(SerialProtocol):
    id = 0xF009

    def __setattr__(self, key, value):
        if value is not None:
            if key == 'configuration':
                data = ACK(self.id).serialize(self.sequence)
                self.dongle.write(data)
                self.dongle.configured = False if value == 1 else True
                self.dongle.boot = True
        self.__dict__[key] = value

    def __init__(self):
        super().__init__(self.id)
        self.register('running', SPType.INT, 1)
        self.register('configuration', SPType.INT, 1)


class SetConfiguration(SerialProtocol):
    id = 0xF00A

    def __init__(self, configuration=False):
        super().__init__(self.id)
        if configuration:
            configuration = 0x02
        else:
            configuration = 0x01
        self.register('configuration', SPType.BOOL, 1, configuration)


@Response
class StatusResponse(SerialProtocol):
    id = 0xF0F0

    def __setattr__(self, key, value):
        if value is not None:
            if key == 'code':
                self.sp_response.code = value
                if value == 0xFE:
                    message = 'Unknown Serial Command'
                elif value == 0xFF:
                    message = 'Unknown Failure'
                elif value == 0:
                    message = ''
                else:
                    message = 'DongleError:'+[
                        "",
                        "Invalid Call",
                        "Invalid Data",
                        "Unsupported",
                        "Endpoint Not Found",
                        "Cluster Not Found",
                        "Attribute Not Found",
                        "Invalid Data Type",
                        "Invalid Length",
                        "Out of Space",
                        "Save Data To Flash Failed",
                        "Get Data From Flash Failed",
                        "Not Found Command In Cluster",
                        "Configuration State Error",
                        "Configured Data Error"
                    ][value]
                self.sp_response.message = message
        self.__dict__[key] = value

    def __init__(self):
        super().__init__(self.id)
        self.register('code', SPType.INT, 1)

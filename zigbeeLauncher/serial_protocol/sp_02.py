from dataclasses import asdict

from dacite import from_dict

from zigbeeLauncher.data_model import ZigbeeInfo, Attribute, Config
from zigbeeLauncher.serial_protocol.sp import SerialProtocol, Response, SPType, encode_int, encode_str, crc_calculate, \
    ACK
from zigbeeLauncher.zigbee.data_type import data_type_name_table, data_type_table, get_data_type


class WriteNodeInfo(SerialProtocol):
    id = 0x0200
    types = ['coordinator', 'router', 'end_device', 'sleepy_end_device']

    def __setattr__(self, key, value):
        if value is not None:
            if key == 'device_type':
                if value == 'unknown':
                    value = 0xFF
                else:
                    value = self.types.index(value)
        self.__dict__[key] = value

    def __init__(self, type=None, power=None, manufacturer_code=None):
        super().__init__(self.id)
        self.register('device_type', SPType.INT, 1, type)
        self.register('radio_power', SPType.INT, 1, power)
        self.register('manufacturer_code', SPType.INT, 2, manufacturer_code)


class GetNodeInfo(SerialProtocol):
    id = 0x0201

    def __init__(self):
        super().__init__(self.id)


@Response
class NodeInfoResponse(SerialProtocol):
    id = 0x0202
    types = ['coordinator', 'router', 'end_device', 'sleepy_end_device']

    def __setattr__(self, key, value):
        if value is not None:
            if key == 'device_type':
                if value == 0xFF:
                    value = 'unknown'
                else:
                    value = self.types[value]
        self.__dict__[key] = value
        if key == 'manufacturer_code' and value is not None:
            self.sp_response.data = {
                "device_type": self.device_type,
                "radio_power": self.radio_power,
                "manufacturer_code": self.manufacturer_code
            }

    def __init__(self):
        super().__init__(self.id)
        self.register('device_type', SPType.INT, 1)
        self.register('radio_power', SPType.INT, 1)
        self.register('manufacturer_code', SPType.INT, 2)


class Cluster(SerialProtocol):
    id = 0

    def __setattr__(self, key, value):
        self.__dict__[key] = value

    @property
    def result(self):
        return {
            'id': self.cluster,
            "manufacturer": True if self.manufacturer_code != 0 else False,
            "manufacturer_code": self.manufacturer_code,
            "attributes": [],
            "commands": {
                "S->C": [],
                "C->S": []
            }
        }

    def __init__(self, cluster=None, manufacturer_code=None):
        super().__init__(self.id)
        self.register('cluster', SPType.INT, 2, cluster)
        self.register('manufacturer_code', SPType.INT, 2, manufacturer_code)


class AddEndpoint(SerialProtocol):
    id = 0x0203

    def __init__(self, endpoint=None, profile=None, device=None, version=None, servers=None, clients=None):
        super().__init__(self.id)
        print(endpoint, profile, device, version, servers, clients)
        self.register('endpoint', SPType.INT, 1, endpoint)
        self.register('profile_id', SPType.INT, 2, profile)
        self.register('device_id', SPType.INT, 2, device)
        self.register('device_version', SPType.INT, 1, version)
        self.register('server_count', SPType.INT, 1, len(servers))
        self.register('client_count', SPType.INT, 1, len(clients))
        self.register('server_clusters', SPType.ARR, 0, servers)
        self.register('client_clusters', SPType.ARR, 0, clients)


class GetEndpoints(SerialProtocol):
    id = 0x0204

    def __init__(self):
        super().__init__(self.id)


class Endpoint(SerialProtocol):
    id = 0

    def __init__(self):
        super().__init__(self.id)
        self.register('endpoint', SPType.INT, 1)


@Response
class EndpointsResponse(SerialProtocol):
    id = 0x0205

    def __setattr__(self, key, value):
        self.__dict__[key] = value
        if key == 'endpoints' and isinstance(value, list):
            self.sp_response.data = [x.endpoint for x in value]

    def __init__(self):
        super().__init__(self.id)
        self.register('count', SPType.INT, 1)
        self.register('endpoints', SPType.ARR, 0, Endpoint, 'count')


class GetEndpointDescriptor(SerialProtocol):
    id = 0x0206

    def __init__(self, endpoint=None):
        super().__init__(self.id)
        self.register('endpoint', SPType.INT, 1, endpoint)


@Response
class EndpointDescriptorResponse(SerialProtocol):
    id = 0x0207

    def __setattr__(self, key, value):
        response = False
        if value is not None:
            if key == 'server_count' and value == 0:
                self.__dict__['server_clusters'] = []
            elif key == 'client_count' and value == 0:
                self.__dict__['client_clusters'] = []
            elif key == 'server_clusters' and isinstance(value, list):
                value = [x.result for x in value]
                if self.client_count == 0:
                    response = True
            elif key == 'client_clusters' and isinstance(value, list):
                value = [x.result for x in value]
                response = True
        self.__dict__[key] = value
        if response:
            self.sp_response.data = self.result

    @property
    def result(self):
        return {
            'id': self.endpoint,
            'profile_id': self.profile_id,
            'device_id': self.device_id,
            'device_version': self.device_version,
            'server_clusters': self.server_clusters,
            'client_clusters': self.client_clusters
        }

    def __init__(self):
        super().__init__(self.id)
        self.register('endpoint', SPType.INT, 1)
        self.register('profile_id', SPType.INT, 2)
        self.register('device_id', SPType.INT, 2)
        self.register('device_version', SPType.INT, 1)
        self.register('server_count', SPType.INT, 1)
        self.register('client_count', SPType.INT, 1)
        self.register('server_clusters', SPType.ARR, 0, Cluster, 'server_count')
        self.register('client_clusters', SPType.ARR, 0, Cluster, 'client_count')


class SPAttribute(SerialProtocol):
    id = 0

    def __setattr__(self, key, value):
        if value is not None:
            if key == 'type':
                id, name, length = get_data_type(id=value)
                value = name
            elif key == 'writable':
                if value & 0x03:
                    value = True
                else:
                    value = False
            elif key == 'length':
                id, name, length = get_data_type(name=self.type)
                del self.attrs[-1]
                # update value record
                if length == 0:
                    # string
                    self.attrs.append(('default', SPType.STR, value, None))
                else:
                    # int
                    self.attrs.append(('default', SPType.INT, value, None))
            elif key == 'default':
                if isinstance(value, str):
                    value = value[1:]
                else:
                    # 判断是否为负数
                    id, name, length = get_data_type(name=self.type)
                    max = (1 << 8 * length) - 1
                    if id in range(0x28, 0x30) and value > max/2:
                        value = -((value - 1) ^ max)

        self.__dict__[key] = value

    @property
    def result(self):
        return {
            "id": self.attribute,
            "manufacturer": True if self.manufacturer_code != 0 else False,
            "manufacturer_code": self.manufacturer_code,
            "type": self.type,
            "writable": self.writable,
            "length": self.length,
            "default": self.default
        }

    def __init__(self, attribute=None, manufacturer_code=None, type=None, writable=None, length=None, default=None):
        super().__init__(self.id)
        self.register('attribute', SPType.INT, 2, attribute)
        self.register('manufacturer_code', SPType.INT, 2, manufacturer_code)
        self.register('type', SPType.INT, 1, type)
        self.register('writable', SPType.INT, 1, writable)
        self.register('length', SPType.INT, 1, length)
        self.register('default', SPType.INT, 0, default)


class SPAttributeWrite(SerialProtocol):
    id = 0

    def __setattr__(self, key, value):
        if value is not None:
            if key == 'type':
                id, name, length = get_data_type(name=value)
                value = id
            elif key == 'writable':
                if value:
                    value = 0x03
                else:
                    value = 0x02
            elif key == 'length':
                id, name, length = get_data_type(id=self.type)
                if length != 0:
                    value = length
            elif key == 'default':
                del self.attrs[-1]
                if isinstance(value, str):
                    self.register('len', SPType.INT, 1, len(value))
                    self.attrs.append(('default', SPType.STR, self.length-1, None))
                else:
                    self.attrs.append(('default', SPType.INT, self.length, None))

        self.__dict__[key] = value

    def __init__(self, attribute=None, manufacturer_code=None, type=None, writable=None, length=None, default=None):
        super().__init__(self.id)
        self.register('attribute', SPType.INT, 2, attribute)
        self.register('manufacturer_code', SPType.INT, 2, manufacturer_code)
        self.register('type', SPType.INT, 1, type)
        self.register('writable', SPType.INT, 1, writable)
        self.register('length', SPType.INT, 1, length)
        self.register('default', SPType.INT, 0, default)


class AddAttributes(SerialProtocol):
    id = 0x0208

    def _encode(self):
        """
        encode attributes to bytes
        :return:
        """
        try:
            len = 0
            data = b''
            attributes_count = 0
            attributes_data = b''
            for attr, type, length, count in self.attrs:
                if attr == 'count':
                    break
                value = getattr(self, attr)
                if type == SPType.BOOL:
                    len += length
                    data += encode_int(int(value), length)
                elif type == SPType.INT:
                    len += length
                    data += encode_int(value, length)
                    pass
            attributes = self.attributes
            for attribute in attributes[:]:
                attribute_len, attribute_data = attribute._encode()
                if len + attribute_len > 180:
                    # 超出长度，分包
                    break
                else:
                    print(f"add attribute:{self.endpoint}, {self.cluster}, {attribute.attribute}")
                    attributes.remove(attribute)
                    len += attribute_len
                    attributes_count += 1
                    attributes_data += attribute_data
            return len+1, data+encode_int(attributes_count, 1)+attributes_data
        except Exception as e:
            print('error:', e)
        # return encode_int(len, 1), data

    def __init__(self, endpoint=None, cluster=None, manufacturer_code=None, server=None,
                 attributes: SPAttributeWrite = None):
        super().__init__(self.id)
        self.register('endpoint', SPType.INT, 1, endpoint)
        self.register('cluster', SPType.INT, 2, cluster)
        self.register('manufacturer_code', SPType.INT, 2, manufacturer_code)
        self.register('server', SPType.BOOL, 1, server)
        self.register('count', SPType.INT, 1, len(attributes))
        self.register('attributes', SPType.ARR, 0, attributes)


class GetAttributes(SerialProtocol):
    id = 0x0209

    def __init__(self, endpoint=None, cluster=None, manufacturer_code=None, server=None):
        super().__init__(self.id)
        self.register('endpoint', SPType.INT, 1, endpoint)
        self.register('cluster', SPType.INT, 2, cluster)
        self.register('manufacturer_code', SPType.INT, 2, manufacturer_code)
        self.register('server', SPType.BOOL, 1, server)


@Response
class AttributesResponse(SerialProtocol):
    id = 0x020A

    def __setattr__(self, key, value):
        self.__dict__[key] = value
        if key == 'attributes' and isinstance(value, list):
            # send ack
            data = ACK(self.id).serialize(self.sequence)
            self.dongle.write(data)
            if self.remains == 0:
                self.dongle.config_attributes.extend([x.result for x in self.attributes])
                self.dongle.config_attributes_done = True
            else:
                # append to self.dongle.config
                self.dongle.config_attributes.extend([x.result for x in self.attributes])

    def __init__(self):
        super().__init__(self.id)
        self.register('endpoint', SPType.INT, 1)
        self.register('cluster', SPType.INT, 2)
        self.register('manufacturer_code', SPType.INT, 2)
        self.register('server', SPType.BOOL, 1)
        self.register('total', SPType.INT, 1)
        self.register('remains', SPType.INT, 1)
        self.register('count', SPType.INT, 1)
        self.register('attributes', SPType.ARR, 0, default_value=SPAttribute, array_count_name='count')


class ReadAttribute(SerialProtocol):
    id = 0x020B

    def __init__(self, endpoint=None, cluster=None, server=None, attribute=None, manufacturer_code=None):
        super().__init__(self.id)
        self.register('endpoint', SPType.INT, 1, endpoint)
        self.register('cluster', SPType.INT, 2, cluster)
        self.register('server', SPType.BOOL, 1, server)
        self.register('attribute', SPType.INT, 2, attribute)
        self.register('manufacturer_code', SPType.INT, 2, manufacturer_code)


@Response
class AttributeResponse(SerialProtocol):
    id = 0x020C

    def __setattr__(self, key, value):
        if value is not None:
            if key == 'manufacturer_code':
                self.manufacturer = False if value == 0 else True
            elif key == 'type':
                # update ('value', type, length)?
                del self.attrs[-1]
                id, name, length = get_data_type(id=value)
                if length == 0:
                    self.register('length', SPType.INT, 1)
                    self.attrs.append(('value', SPType.STR, 0, None))
                else:
                    self.attrs.append(('value', SPType.INT, length, None))
                value = name
            elif key == "value":
                if isinstance(value, str):
                    # value = value[1:]
                    pass
                else:
                    # 判断是否为负数
                    id, name, length = get_data_type(name=self.type)
                    max = (1 << 8 * length) - 1
                    if id in range(0x28, 0x30) and value > max/2:
                        value = -((value - 1) ^ max)

        self.__dict__[key] = value
        if key == 'value' and value is not None:
            self.sp_response.data = asdict(from_dict(data_class=Attribute, data=self.__dict__))

    def __init__(self):
        super().__init__(self.id)
        self.register('endpoint', SPType.INT, 1)
        self.register('cluster', SPType.INT, 2)
        self.register('server', SPType.BOOL, 1)
        self.register('attribute', SPType.INT, 2)
        self.register('manufacturer_code', SPType.INT, 2)
        self.register('properties', SPType.INT, 1)
        self.register('type', SPType.INT, 1)
        self.register('value', SPType.INT, 0)


class WriteAttribute(SerialProtocol):
    id = 0x020D

    def __setattr__(self, key, value):
        if value is not None:
            if key == 'type':
                id, name, length = get_data_type(name=value)
                value = id
            elif key == 'value':
                del self.attrs[-1]
                id, name, length = get_data_type(id=self.type)
                if length == 0:
                    self.length = 0
                    self.register('length', SPType.INT, 1, len(value) + 1)
                    self.attrs.append(('value', SPType.STR, len(value) + 1, None))
                else:
                    self.attrs.append(('value', SPType.INT, length, None))
        self.__dict__[key] = value

    def __init__(self, endpoint=None, cluster=None, server=None, attribute=None, manufacturer_code=None, type=None,
                 value=None):
        super().__init__(self.id)
        self.register('endpoint', SPType.INT, 1, endpoint)
        self.register('cluster', SPType.INT, 2, cluster)
        self.register('server', SPType.BOOL, 1, server)
        self.register('attribute', SPType.INT, 2, attribute)
        self.register('manufacturer_code', SPType.INT, 2, manufacturer_code)
        self.register('type', SPType.INT, 1, type)
        self.register('value', SPType.INT, 0, value)


class WriteDefaultValue(SerialProtocol):
    id = 0x020E

    def __init__(self, attribute: WriteAttribute = None):
        super().__init__(self.id)
        self.register('attribute', SPType.OBJ, 0, attribute)


class SPCommand(SerialProtocol):
    id = 0

    @property
    def result(self):
        return {
            "id": self.command,
            "manufacturer": True if self.manufacturer_code != 0 else False,
            "manufacturer_code": self.manufacturer_code
        }

    def __init__(self, command=None, mask=None, manufacturer_code=None):
        super().__init__(self.id)
        self.register('command', SPType.INT, 1, command)
        self.register('mask', SPType.INT, 1, mask)
        self.register('manufacturer_code', SPType.INT, 2, manufacturer_code)


class AddCommands(SerialProtocol):
    id = 0x020F

    def __init__(self, endpoint=None, cluster=None, manufacturer_code=None, server=None, commands: SPCommand = None):
        super().__init__(self.id)
        self.register('endpoint', SPType.INT, 1, endpoint)
        self.register('cluster', SPType.INT, 2, cluster)
        self.register('manufacturer_code', SPType.INT, 2, manufacturer_code)
        self.register('server', SPType.BOOL, 1, server)
        self.register('count', SPType.INT, 1, len(commands))
        self.register('commands', SPType.ARR, 0, commands, 'count')


class GetCommands(SerialProtocol):
    id = 0x0210

    def __init__(self, endpoint=None, cluster=None, manufacturer_code=None, server=None):
        super().__init__(self.id)
        self.register('endpoint', SPType.INT, 1, endpoint)
        self.register('cluster', SPType.INT, 2, cluster)
        self.register('manufacturer_code', SPType.INT, 2, manufacturer_code)
        self.register('server', SPType.BOOL, 1, server)


@Response
class CommandsResponse(SerialProtocol):
    id = 0x0211

    def __setattr__(self, key, value):
        self.__dict__[key] = value
        if key == 'commands' and isinstance(value, list):
            self.dongle.config_commands = [x.result for x in value]

    def __init__(self):
        super().__init__(self.id)
        self.register('endpoint', SPType.INT, 1)
        self.register('cluster', SPType.INT, 2)
        self.register('manufacturer_code', SPType.INT, 2)
        self.register('server', SPType.BOOL, 1)
        self.register('total', SPType.INT, 1)
        self.register('remains', SPType.INT, 1)
        self.register('count', SPType.INT, 1)
        self.register('commands', SPType.ARR, 0, SPCommand, 'count')

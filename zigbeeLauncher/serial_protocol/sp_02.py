from dataclasses import asdict

from dacite import from_dict

from zigbeeLauncher.data_model import ZigbeeInfo, Attribute, Config
from zigbeeLauncher.serial_protocol.sp import SerialProtocol, Response, SPType
from zigbeeLauncher.zigbee.data_type import data_type_name_table, data_type_table, get_data_type


class WriteNodeInfo(SerialProtocol):
    id = 0x0200
    types = ['coordinator', 'router', 'end_device', 'sleepy_end_device']

    def __setattr__(self, key, value):
        if value is not None:
            if key == 'type':
                if value == 'unknown':
                    value = 0xFF
                else:
                    value = self.types.index(value)
        self.__dict__[key] = value

    def __init__(self, type=None, power=None, manufacturer_code=None):
        super().__init__(self.id)
        self.register('type', SPType.INT, 1, type)
        self.register('power', SPType.INT, 1, power)
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
            if key == 'type':
                if value == 0xFF:
                    value = 'unknown'
                else:
                    value = self.types[value]
        self.__dict__[key] = value
        if key == 'manufacturer_code' and value is not None:
            self.sp_response.data = self.__dict__

    def __init__(self):
        super().__init__(self.id)
        self.register('device_type', SPType.INT, 1)
        self.register('radio_power', SPType.INT, 1)
        self.register('manufacturer_code', SPType.INT, 2)


class Cluster(SerialProtocol):
    id = 0

    def __setattr__(self, key, value):
        if value is not None:
            if key == 'manufacturer_code':
                if value != 0:
                    self.__dict__['manufacturer'] = True
                else:
                    self.__dict__['manufacturer'] = False
                self.__dict__['attributes'] = []
                self.__dict__['commands'] = []
        self.__dict__[key] = value

    @property
    def cluster(self):
        return self.__dict__

    def __init__(self, cluster=None, manufacturer_code=None):
        super().__init__(self.id)
        self.register('id', SPType.INT, 2, cluster)
        self.register('manufacturer_code', SPType.INT, 2, manufacturer_code)


class AddEndpoint(SerialProtocol):
    id = 0x0203

    def __init__(self, endpoint=None, profile=None, device=None, version=None, servers=None, clients=None):
        super().__init__(self.id)
        self.register('id', SPType, 1, endpoint)
        self.register('profile_id', SPType, 2, profile)
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
        if key == 'endpoint' and value is not None:
            self.sp_response.data = [x.endpoint for x in self.endpoints]

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
            if key == 'client_count' and value == 0:
                self.__dict__['client_clusters'] = []
            elif key == 'server_clusters':
                value = [x.cluster for x in self.server_clusters]
                if self.client_count == 0:
                    response = True
            elif key == 'client_clusters':
                value = [x.cluster for x in self.client_clusters]
                response = True
        self.__dict__[key] = value
        if response:
            self.sp_response.data = self.__dict__

    def __init__(self):
        super().__init__(self.id)
        self.register('id', SPType.INT, 1)
        self.register('profile_id', SPType, 2)
        self.register('device_id', SPType.INT, 2)
        self.register('device_version', SPType.INT, 1)
        self.register('server_count', SPType.INT, 1)
        self.register('client_count', SPType.INT, 1)
        self.register('server_cluster', SPType.ARR, 0, Cluster, 'server_count')
        self.register('client_cluster', SPType.ARR, 0, Cluster, 'client_count')


class SPAttribute(SerialProtocol):
    id = 0

    def __setattr__(self, key, value):
        if value is not None:
            if key == 'manufacturer_code':
                if value != 0:
                    self.__dict__['manufacturer'] = True
                else:
                    self.__dict__['manufacturer'] = False
            elif key == 'type':
                id, name, length = get_data_type(name=value)
                value = id
            elif key == 'length':
                self.len = 7 + value
                id, name, length = get_data_type(id=self.type)
                del self.attrs[-1]
                # update value record
                if length == 0:
                    # string
                    self.attrs.append(('default', SPType.STR, value, None))
                else:
                    # int
                    self.attrs.append(('default', SPType.INT, value, None))
        self.__dict__[key] = value

    @property
    def attribute(self):
        return self.__dict__

    def __init__(self, attribute=None, manufacturer_code=None, type=None, writable=None, length=None, default=None):
        super().__init__(self.id)
        self.register('id', SPType.INT, 2, attribute)
        self.register('manufacturer_code', SPType.INT, 2, manufacturer_code)
        self.register('type', SPType.INT, 1, type)
        self.register('writable', SPType.INT, 1, writable)
        self.register('length', SPType.INT, 1, length)
        self.register('default', SPType.INT, 0, default)


class AddAttributes(SerialProtocol):
    id = 0x0208

    def __init__(self, endpoint=None, cluster=None, manufacturer_code=None, server=None,
                 attributes: SPAttribute = None):
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
        if key == 'attributes' and value is not None:
            if self.remains == 0:
                self.dongle.config_attributes.extend([x.attribute for x in self.attributes])
                self.dongle.config_attributes_done = True
            else:
                # append to self.dongle.config
                self.dongle.config_attributes.extend([x.attribute for x in self.attributes])

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
                    self.attrs.append(('value', SPType.STR, len(value) + 1), None)
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

    def __init__(self, attribute: WriteAttribute=None):
        super().__init__(self.id)
        self.register('attribute', SPType.OBJ, 0, attribute)


class SPCommand(SerialProtocol):
    id = 0

    def __init__(self, command=None, mask=None, manufacturer_code=None):
        super().__init__(self.id)
        self.register('command', SPType.INT, 1, command)
        self.register('mask', SPType.INT, 1, mask)
        self.register('manufacturer_code', SPType.INT, 2, manufacturer_code)


class AddCommands(SerialProtocol):
    id = 0x020F

    def __init__(self, endpoint=None, cluster=None, manufacturer_code=None, server=None, commands:SPCommand=None):
        super().__init__(self.id)
        self.register('endpoint', SPType.INT, 1, endpoint)
        self.register('cluster', SPType.INT, 2, cluster)
        self.register('manufacturer_code', SPType.INT, 2, manufacturer_code)
        self.register('server', SPType.BOOL, 1, server)
        self.register('count', SPType.INT, 1, len(commands))
        self.register('commands', SPType.ARR, SPCommand.len, SPCommand, commands)


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
        if key == 'commands' and value is not None:
            self.sp_response.data = self

    def __init__(self):
        super().__init__(self.id)
        self.register('endpoint', SPType.INT, 1)
        self.register('cluster', SPType.INT, 2)
        self.register('manufacturer_code', SPType.INT, 2)
        self.register('server', SPType.BOOL, 1)
        self.register('total', SPType.INT, 1)
        self.register('remains', SPType.INT, 1)
        self.register('count', SPType.INT, 1)
        self.register('commands', SPType.ARR, SPCommand.len, SPCommand, 'count')

from dataclasses import dataclass, field
from typing import Optional, Any

from dacite import from_dict

from zigbeeLauncher.database.interface import DBDevice, DBSimulator, DBZigbee


@dataclass
class Message:
    uuid: str
    timestamp: int
    data: Any
    code: Optional[int]
    message: Optional[str]


@dataclass
class ErrorMessage(Message):
    code: int
    message: str


@dataclass
class Sync:
    ip: str


@dataclass
class ZigbeeInfo(DBZigbee.DataModel):
    pass


@dataclass
class DeviceInfo(DBDevice.DataModel):
    zigbee: ZigbeeInfo
    device: DBDevice.DataModel = field(init=False)

    def __post_init__(self):
        self.device = from_dict(data_class=DBDevice.DataModel, data=self.__dict__)


@dataclass
class SimulatorInfo(DBSimulator.DataModel):
    devices: list[DeviceInfo]
    simulator: DBSimulator.DataModel = field(init=False)

    def __post_init__(self):
        self.simulator = from_dict(data_class=DBSimulator.DataModel, data=self.__dict__)


@dataclass
class Firmware:
    filename: str


@dataclass
class Label:
    data: str


@dataclass
class Join:
    channels: list[int]
    pan_id: Optional[int]
    extended_pan_id: Optional[int]


@dataclass
class Attribute:
    endpoint: int
    cluster: int
    server: bool
    manufacturer: bool
    attribute: int
    manufacturer_code: Optional[int] = field(default=0)
    type: Optional[str] = field(default=None)
    value: Optional[Any] = field(default=None)


@dataclass
class Config:
    @dataclass
    class ConfigNode:
        device_type: str
        manufacturer_code: int
        radio_power: int

    @dataclass
    class Endpoint:
        @dataclass
        class Cluster:
            @dataclass
            class Attribute:
                id: int
                manufacturer: int
                manufacturer_code: Optional[int]
                type: str
                writable: bool
                length: Optional[int]
                default: Any
                name: Optional[str]

            @dataclass
            class Command:
                id: int
                manufacturer: bool
                manufacturer_code: Optional[int]
                description: Optional[str]

            id: int
            manufacturer: bool
            manufacturer_code: Optional[int]
            name: Optional[str]
            attributes: list[Attribute]
            commands: Any
            server_commands: list[Command] = field(init=False)
            client_commands: list[Command] = field(init=False)

            def __post_init__(self):
                self.server_commands = []
                self.client_commands = []
                server_commands = self.commands.get('S->C')
                print(f"self.commands.get('S->C'):{self.commands.get('S->C')}")
                if server_commands:
                    for command in server_commands:
                        print(f"{self.id}, command:{command}")
                        self.server_commands.append(from_dict(data_class=self.Command, data=command))
                print(f"{self.id}, server_commands:{self.server_commands}")
                client_commands = self.commands.get('C->S')
                print(f"self.commands.get('C->S'):{self.commands.get('C->S')}")
                if client_commands:
                    for command in client_commands:
                        print(f"{self.id}, command:{command}")
                        self.client_commands.append(from_dict(data_class=self.Command, data=command))
                print(f"{self.id}, client_commands:{self.client_commands}")

        id: int
        profile_id: int
        device_id: int
        device_version: int
        server_clusters: list[Cluster]
        client_clusters: list[Cluster]

    node: ConfigNode
    endpoints: list[Endpoint]


@dataclass
class CommandSimulator:
    @dataclass
    class FirmwareSimulator(Firmware):
        devices: list[str]

    @dataclass
    class ConfigSimulator:
        config: Config
        devices: list[str]

    firmware: Optional[FirmwareSimulator]
    label: Optional[Label]
    config: Optional[ConfigSimulator]


@dataclass
class CommandDevice:
    firmware: Optional[Firmware] = field(default=None)
    label: Optional[Label] = field(default=None)
    config: Optional[Config] = field(default=None)
    get_config: Optional[Any] = field(default=None)

    identify: Optional[Any] = field(default=None)
    reset: Optional[Any] = field(default=None)
    join: Optional[Join] = field(default=None)
    leave: Optional[Any] = field(default=None)
    data_request: Optional[Any] = field(default=None)
    attribute: Optional[Attribute] = field(default=None)

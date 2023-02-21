import asyncio
import time
from dataclasses import dataclass, asdict
from functools import wraps

from zeroconf import ServiceBrowser, ServiceInfo, Zeroconf, IPVersion

from zigbeeLauncher.database.interface import DBSimulator, DBDevice
from zigbeeLauncher.dongle.management import init
from zigbeeLauncher.simulator.client import ZLTHClient
from zigbeeLauncher.data_model import SimulatorInfo
from zigbeeLauncher.tasks import Tasks
from zigbeeLauncher.util import get_ip_address, get_mac_address, Global
from zigbeeLauncher.logging import mqttLogger as logger


@dataclass
class Broker:
    ip: str
    timestamp: int


class ServicesListener:

    brokers=[]

    def get_broker(self, ip):
        for index, broker in enumerate(self.brokers):
            if broker.ip == ip:
                return index
        return -1

    def remove_service(self, zeroconf, type, name):
        info = zeroconf.get_service_info(type, name)
        logger.info("Service %s removed, service info: %s", name, info)
        for addr in info.parsed_scoped_addresses():
            index = self.get_broker(addr)
            if index != -1:
                self.brokers.pop(index)
        Global.get(Global.SIMULATOR).on_service_update(sorted(self.brokers, key=lambda x: x.timestamp))

    def add_service(self, zeroconf, type, name):
        info = zeroconf.get_service_info(type, name)
        logger.info("Service %s added, service info: %s", name, info)
        timestamp = int(info.properties.get(b'timestamp').decode())
        for addr in info.parsed_scoped_addresses():
            index = self.get_broker(addr)
            if index == -1:
                logger.info(f"service timestamp:{timestamp}")
                broker = Broker(ip=addr, timestamp=timestamp)
                self.brokers.append(broker)
                print("brokers:", sorted(self.brokers, key=lambda x: x.timestamp))
        Global.get(Global.SIMULATOR).on_service_update(sorted(self.brokers, key=lambda x: x.timestamp))

    def update_service(self, zeroconf, type, name):
        info = zeroconf.get_service_info(type, name)
        logger.info("Service %s updated, service info:%s", name, info)
        timestamp = int(info.properties.get(b'timestamp').decode())
        for addr in info.parsed_scoped_addresses():
            index = self.get_broker(addr)
            if index != -1:
                self.brokers[index].timestamp = timestamp
        Global.get(Global.SIMULATOR).on_service_update(sorted(self.brokers, key=lambda x: x.timestamp))


class SimulatorMetaData:
    def __init__(self, ip, mac, label, version, update_cb):
        self.update_cb = update_cb
        Global.set(Global.DONGLES, {})
        self._info = SimulatorInfo(
            ip=ip,
            mac=mac,
            label=label,
            version=version,
            name='simulator-'+ip,
            connected=True,
            broker="",
            devices=[]
        )

    @staticmethod
    def update(func):
        @wraps(func)
        def decorator(*args, **kwargs):
            func(*args, **kwargs)
            args[0].update_cb({func.__code__.co_varnames[1]: args[1]})

        return decorator

    @property
    def info(self):
        self._info.devices = []
        for _, dongle in Global.get(Global.DONGLES).items():
            self._info.devices.append(dongle.info)
        return self._info

    @property
    def ip(self):
        return self._info.ip

    @ip.setter
    @update
    def ip(self, ip):
        self._info.ip = ip
        self._info.simulator.ip = ip
        self._info.name = 'simulator-'+self.ip
        self._info.simulator.name = self._info.name

    @property
    def name(self):
        return self._info.name

    @property
    def mac(self):
        return self._info.mac

    @property
    def label(self):
        return self._info.label

    @label.setter
    @update
    def label(self, label):
        self._info.label = label
        self._info.simulator.label = label

    @property
    def broker(self):
        return self._info.broker

    @broker.setter
    @update
    def broker(self, broker):
        self._info.broker = broker
        self._info.simulator.broker = broker

    @property
    def devices(self):
        return self._info.devices

    @devices.setter
    @update
    def devices(self, devices):
        self._info.devices = devices


class Simulator(SimulatorMetaData):
    # _instance = None
    # _flag = False

    # def __new__(cls, *args, **kwargs):
    #     if cls._instance is None:
    #         cls._instance = super().__new__(cls, *args, **kwargs)
    #     return cls._instance

    def __init__(self, ip=None, mac=None, label=None, version=None):
        super().__init__(ip, mac, label, version, self._update)

        self._zeroconf = None
        self.client = None
        self._service_browser = None
        self._retry = 0
        self._brokers = None

        self._register()

        tasks = Tasks()
        tasks.add(self._ip_change_monitor())

    async def _ip_change_monitor(self):
        while True:
            ip = get_ip_address()
            if ip != self.ip:
                # update local simulator ip and name
                DBSimulator(ip=self.ip).update({
                    'ip': ip,
                    'name': 'simulator-' + ip
                })
                DBDevice(ip=self.ip).update({'ip': ip})
                simulators = DBSimulator().retrieve()
                for item in simulators:
                    if item['ip'] != ip:
                        DBSimulator(ip=item['ip']).update({'connected': False})
                        DBDevice(ip=item['ip']).update({'connected': False})
                logger.warning("ip change from %s to %s", self.ip, ip)
                self.ip = ip
                simulators = DBSimulator().retrieve()
                for simulator in simulators:
                    print(simulator)

                # self.update(ip=ip, _name='simulator-' + ip)
                self._unregister()
                self._register()

            else:
                await asyncio.sleep(5)

    def _register(self):
        timestamp = int(time.time() * 1000 * 1000)
        logger.info(f"Register mdns service, timestamp: {timestamp}")

        info = ServiceInfo(
            "_launcher._tcp.local.",
            self.mac + "._launcher._tcp.local.",
            addresses=[get_ip_address()],
            port=1883,
            properties={'timestamp': timestamp},
            server=str(get_mac_address()) + '.local.',
        )
        self._zeroconf = Zeroconf(ip_version=IPVersion.All)
        self._zeroconf.register_service(info)

        self._service_browser = ServiceBrowser(Zeroconf(), "_launcher._tcp.local.", ServicesListener())

    def _unregister(self):
        self.client.disconnect()
        self._service_browser.cancel()
        self._zeroconf.remove_all_service_listeners()
        self._zeroconf.unregister_service(self.info)
        self._zeroconf.close()

    def on_service_update(self, brokers):
        # connect to the first broker
        if not brokers:
            logger.warning('not available MQTT broker, try later')
            return
        self._brokers = brokers
        ip = self._brokers[0].ip
        if self.broker != ip:
            self.broker = ip
            if self.client:
                self.client.stop()
                self.client = None
            else:
                self.client = ZLTHClient(broker=self.broker, name=self.name, connection_cb=self._on_connection)

    def _on_connection(self, connected):
        if connected:
            logger.info(f'connected to broker:{self.broker}')
            self._retry = 0
            # initial dongle management
            init()
        else:
            if self._retry == 10:

                # stop current connection
                if self.client:
                    self.client.stop()
                    self.client = None
                if len(self._brokers) > 1:
                    # connect to next brokers
                    logger.error(f'lost broker connection, try another broker')
                    self._brokers.pop(0)
                else:
                    logger.info(f'keep retry')
                    self._retry = 0

                self.on_service_update(self._brokers)
            else:
                logger.warning(f'lost broker connection, retry:{self._retry}')
                self._retry += 1

    def _update(self, data):
        if self.client:
            self.client.send_simulator_update(data)

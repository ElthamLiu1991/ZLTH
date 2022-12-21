import asyncio
import threading
import time

from zeroconf import ServiceBrowser, ServiceInfo, Zeroconf, IPVersion

from zigbeeLauncher.database.interface import DBSimulator, DBDevice
from zigbeeLauncher.dongle import init
from zigbeeLauncher.dongle.Dongle import dongles
from zigbeeLauncher.mqtt.Service import ServicesListener
from zigbeeLauncher.mqtt.Callbacks import simulator_update_callback, simulator_info_callback
from zigbeeLauncher.mqtt.Connection import ZLTHMQTT
from zigbeeLauncher.util import get_ip_address, get_mac_address
from zigbeeLauncher.logging import mqttLogger as logger


class Simulator(threading.Thread):

    _instance = None
    _flag = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance=super().__new__(cls)
        return cls._instance

    def __init__(self, ip='', mac='', label='', version='0.0.0'):
        if not self._flag:
            self._flag = True
            threading.Thread.__init__(self)
            self.ip = ip
            self.name = 'simulator-' + self.ip
            self.mac = mac
            self.connected = True
            self.label = label
            self.version = version

            self.zeroconf = None
            self.info = None
            self.client = None  # localhost mqtt client
            self.service_browser = None
            self.register()
            init()

    def run(self):
        while True:
            ip_new = get_ip_address()
            if ip_new != self.ip:
                # update local simulator ip and name
                DBSimulator(ip=self.ip).update({
                    'ip': ip_new,
                    'name': 'simulator-'+ip_new
                })
                DBDevice(ip=self.ip).update({'ip': ip_new})
                simulators = DBSimulator().retrieve()
                for item in simulators:
                    if item['ip'] != ip_new:
                        DBSimulator(ip=item['ip']).update({'connected': False})
                        DBDevice(ip=item['ip']).update({'connected': False})
                logger.warning("ip change from %s to %s", self.ip, ip_new)
                simulators = DBSimulator().retrieve()
                for simulator in simulators:
                    print(simulator)
                self.update(ip=ip_new, _name='simulator-' + ip_new)
                self.unregister()
                self.register()

            else:
                time.sleep(0.5)

    def register(self):
        logger.info("Run MQTT client: simulator")
        thread = ZLTHMQTT('127.0.0.1', 1883, 'simulator', self.on_connected)
        thread.start()
        self.service_browser = ServiceBrowser(Zeroconf(), "_launcher._tcp.local.", ServicesListener())
        self.info = ServiceInfo(
            "_launcher._tcp.local.",
            self.mac + "._launcher._tcp.local.",
            addresses=[get_ip_address()],
            port=1883,
            properties={'timestamp': round(int(time.time() * 1000 * 1000))},
            server=str(get_mac_address()) + '.local.',
        )
        self.zeroconf = Zeroconf(ip_version=IPVersion.All)
        self.zeroconf.register_service(self.info)

    def unregister(self):
        self.client.disconnect()
        self.service_browser.cancel()
        self.zeroconf.remove_all_service_listeners()
        self.zeroconf.unregister_service(self.info)

    def on_connected(self, client):
        self.client = client
        simulator_info_callback(self.get())

    def update(self, **kwargs):
        payload = {}
        for key, value in kwargs.items():
            if key in self.__dict__ and value != self.__dict__[key]:
                if key == '_name':
                    key = 'name'
                payload.update({key: value})
        self.__dict__.update(kwargs)
        if payload != {}:
            simulator_update_callback(payload)

    def get(self):
        data = {
            "ip": self.ip,
            "mac": self.mac,
            "name": self.name,
            "connected": self.connected,
            "label": self.label,
            "version": self.version
        }
        devices = []
        for item in dongles:
            dongle = dongles[item]
            if dongle.property.ready:
                device = dongle.property.get()
                device['ip'] = self.ip
                devices.append(device)
        data['devices'] = devices
        return data

import threading
import time

from zeroconf import ServiceBrowser, ServiceInfo, Zeroconf, IPVersion

from zigbeeLauncher.database.interface import DBSimulator, DBDevice
from zigbeeLauncher.dongle.Dongle import dongles
from zigbeeLauncher.mqtt.Service import ServicesListener
from zigbeeLauncher.mqtt.Callbacks import simulator_update_callback
from zigbeeLauncher.mqtt.Instance import WiserMQTT, brokers
from zigbeeLauncher.util import get_ip_address, get_mac_address, set_value
from zigbeeLauncher.logging import mqttLogger as logger


class Simulator(threading.Thread):
    def __init__(self, ip, mac, label='', version='0.0.0'):
        threading.Thread.__init__(self)
        self.ip = ip
        self.name = 'simulator-' + self.ip
        self.mac = mac
        self.connected = True
        self.label = label
        self.version = version

        self.zeroconf = None
        self.info = None
        self.client = None
        self.register()

    def run(self):
        while True:
            ip_new = get_ip_address()
            if ip_new != self.ip:
                set_value('client_ip', ip_new)
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
                del brokers[self.ip]
                self.unregister()
                self.register()
                self.update(ip=ip_new, name='simulator-'+ip_new)
            else:
                time.sleep(1)

    def register(self):
        logger.info("Run MQTT client: simulator")
        thread = WiserMQTT('127.0.0.1', 1883, 'simulator', self.on_connected)
        thread.start()
        ServiceBrowser(Zeroconf(), "_launcher._tcp.local.", ServicesListener())
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
        self.zeroconf.remove_all_service_listeners()
        self.zeroconf.unregister_service(self.info)

    def on_connected(self, client):
        self.client = client

    def update(self, **kwargs):
        payload = {}
        for key in kwargs:
            if key in self.__dict__ and kwargs[key] != self.__dict__[key]:
                payload.update({key: kwargs[key]})
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

import socket
import time

from zeroconf import ServiceBrowser, Zeroconf, ServiceInfo, IPVersion


class MyListener:

    def remove_service(self, zeroconf, type, name):
        print("Service %s removed" % (name,))

    def add_service(self, zeroconf, type, name):
        info = zeroconf.get_service_info(type, name)
        print("Service %s added, service info: %s" % (name, info))



zeroconf = Zeroconf()

listener = MyListener()
browser = ServiceBrowser(zeroconf, "_miio._udp.local.", listener)

desc = {'Hello': 'World'}

info = ServiceInfo(
    "_launcher._tcp.local.",
    "Wiser Zigbee Launcher._launcher._tcp.local.",
    addresses=[socket.inet_aton("127.0.0.1")],
    port=80,
    properties=desc,
    server="ash-2.local.",
)

zeroconf = Zeroconf(ip_version=IPVersion.All)
print("Registration of a service, press Ctrl-C to exit...")
zeroconf.register_service(info)
try:
    while True:
        time.sleep(0.1)
except KeyboardInterrupt:
    pass
finally:
    zeroconf.close()

from flask_mqtt import Mqtt
from . import mqtt_version, router
from . import WiserZigbeeLauncher
from .WiserZigbeeGlobal import set_value


def init(app):
    if not app:
        print("app is None, cannot start MQTT client")
        return None
    set_value("app", app)
    mqtt = Mqtt(app)

    @mqtt.on_connect()
    def on_connect(client, userdata, flags, rc):
        print("on_connect, rc: %s" % rc)
        client.subscribe(mqtt_version + "/+/simulator/devices/+/error")
        client.subscribe(mqtt_version + "/+/simulator/info")
        client.subscribe(mqtt_version + "/+/simulator/devices/+/info")
        client.subscribe(mqtt_version + "/+/simulator/update")
        client.subscribe(mqtt_version + "/+/simulator/devices/+/update")

        # request all simulator info
        WiserZigbeeLauncher.request_simulator_info(client)

    @mqtt.on_subscribe()
    def on_subscribe(client, userdata, mid, granted_qos):
        print("on_subscribe: qos=%d" % granted_qos)

    @mqtt.on_message()
    def on_message(client, userdata, message):
        print("on_message: %s, %s" % (message.topic, message.payload.decode()))
        topic = message.topic[message.topic.find("/", 10):]
        print(topic)
        router.call(topic, client, message.payload.decode('utf-8'))

    @mqtt.on_disconnect()
    def on_disconnect():
        print("on_disconnect")
from zigbeeLauncher.util import pack_payload
from zigbeeLauncher.logging import simulatorLogger as logger


def simulator_info_callback(payload):
    from zigbeeLauncher.mqtt.Simulator import Simulator
    simulator = Simulator()
    data = pack_payload(payload)
    if simulator.client:
        from zigbeeLauncher.mqtt import mqtt_version
        topic = mqtt_version + "/simulator/info"
        logger.info("Publish: topic:%s, payload:%s", topic, data)
        simulator.client.publish(topic, data, qos=2)
    else:
        logger.error("MQTT client is not ready")
        # insert to database
        from .Simulator_API import simulator_info
        simulator_info(None, simulator.ip, data)


def simulator_update_callback(payload):
    from zigbeeLauncher.mqtt.Simulator import Simulator
    simulator = Simulator()
    data = pack_payload(payload)
    if simulator.client:
        from zigbeeLauncher.mqtt import mqtt_version
        topic = mqtt_version + "/simulator/update"
        logger.info("Publish: topic:%s, payload:%s", topic, data)
        simulator.client.publish(topic, data, qos=2)
    else:
        logger.error("MQTT client is not ready")
        # insert to database
        # from .Simulator_API import simulator_update
        # simulator_update(None, simulator.ip, data)


def simulator_error_callback(code=0, message='', payload={}, timestamp=0, uuid=''):
    msg = {
        'code': code,
        'message': message,
        'data': payload,
        'timestamp': timestamp,
        'uuid': uuid
    }
    data = pack_payload(msg)
    from zigbeeLauncher.mqtt.Simulator import Simulator
    simulator = Simulator()
    if simulator.client:
        from zigbeeLauncher.mqtt import mqtt_version
        topic = mqtt_version + "/simulator/error"
        logger.info("Publish: topic:%s", topic)
        simulator.client.publish(topic, data, qos=2)
    else:
        logger.error("MQTT client is not ready")


def dongle_info_callback(device='', payload={}, **kwargs):
    from zigbeeLauncher.mqtt.Simulator import Simulator
    simulator = Simulator()
    payload["ip"] = simulator.ip
    data = pack_payload(payload)
    if simulator.client:
        from zigbeeLauncher.mqtt import mqtt_version
        topic = mqtt_version + "/simulator/devices/" + device + "/info"
        logger.info("Publish: topic:%s, payload:%s", topic, data)
        simulator.client.publish(topic, data, qos=2)
    else:
        logger.error("MQTT client is not ready")
        # insert to database
        # from .Simulator_API import simulator_device_info
        # simulator_device_info(None, simulator.ip, data, device)


def dongle_update_callback(device, payload):
    from zigbeeLauncher.mqtt.Simulator import Simulator
    simulator = Simulator()
    data = pack_payload(payload)
    if simulator.client:
        from zigbeeLauncher.mqtt import mqtt_version
        topic = mqtt_version + "/simulator/devices/" + device + "/update"
        logger.info("Publish: topic:%s, payload:%s", topic, data)
        simulator.client.publish(topic, data, qos=2)
    else:
        logger.error("MQTT client is not ready")
        # insert to database
        # from .Simulator_API import simulator_device_update
        # simulator_device_update(None, simulator.ip, data, device)


def dongle_error_callback(device='', code=0, message='', payload={}, timestamp=0, uuid='', **kwargs):
    msg = {
        'code': code,
        'message': message,
        'data': payload,
        'timestamp': timestamp,
        'uuid': uuid
    }
    data = pack_payload(msg)

    from zigbeeLauncher.mqtt.Simulator import Simulator
    simulator = Simulator()
    if simulator.client:
        from zigbeeLauncher.mqtt import mqtt_version
        topic = mqtt_version + "/simulator/devices/" + device + "/error"
        logger.info("Publish: topic:%s, %s", topic, data)
        simulator.client.publish(topic, data, qos=2)
    else:
        logger.error("MQTT client is not ready")

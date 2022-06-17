from zigbeeLauncher.util import pack_payload, get_ip_address, get_value
# from zigbeeLauncher.mqtt.Launcher_API import simulator_device_update, simulator_device_info
from zigbeeLauncher.logging import simulatorLogger as logger
from zigbeeLauncher.mqtt.Instance import brokers


def simulator_info_callback(payload):
    data = pack_payload(payload)
    topic = get_value('mqtt_version') + "/simulator/info"
    logger.info("Publish: topic:%s, payload:%s", topic, data)
    if brokers and get_value('client_ip') in brokers:
        brokers[get_value('client_ip')].publish(topic, data, qos=2)
    else:
        logger.error("MQTT client is not ready")
        # insert to database
        from .Simulator_API import simulator_info
        simulator_info(None, get_value('client_ip'), data)


def simulator_update_callback(payload):
    data = pack_payload(payload)
    topic = get_value('mqtt_version') + "/simulator/update"
    logger.info("Publish: topic:%s, payload:%s", topic, data)
    if brokers and get_value('client_ip') in brokers:
        brokers[get_value('client_ip')].publish(topic, data, qos=2)
    else:
        logger.error("MQTT client is not ready")
        # insert to database
        from .Simulator_API import simulator_update
        simulator_update(None, get_value('client_ip'), data)


def simulator_error_callback(code=0, message='', payload={}, timestamp=0, uuid=''):
    msg = {
        'code': code,
        'message': message,
        'response': payload,
        'timestamp': timestamp,
        'uuid': uuid
    }
    data = pack_payload(msg)
    topic = get_value('mqtt_version') + "/simulator/error"
    logger.info("Publish: topic:%s", topic)
    if brokers and get_value('client_ip') in brokers:
        brokers[get_value('client_ip')].publish(topic, data, qos=2)
    else:
        logger.error("MQTT client is not ready")


def dongle_info_callback(device='', payload={}, **kwargs):
    payload["ip"] = get_value('client_ip')
    data = pack_payload(payload)
    topic = get_value('mqtt_version') + "/simulator/devices/" + device + "/info"
    logger.info("Publish: topic:%s, payload:%s", topic, data)
    if brokers and get_value('client_ip') in brokers:
        brokers[get_value('client_ip')].publish(topic, data, qos=2)
    else:
        logger.error("MQTT client is not ready")
        # insert to database
        from .Simulator_API import simulator_device_info
        simulator_device_info(None, get_value('client_ip'), data, device)


def dongle_update_callback(device, payload):
    data = pack_payload(payload)
    topic = get_value('mqtt_version') + "/simulator/devices/" + device + "/update"
    logger.info("Publish: topic:%s, payload:%s", topic, data)
    if brokers and get_value('client_ip') in brokers:
        brokers[get_value('client_ip')].publish(topic, data, qos=2)
    else:
        logger.error("MQTT client is not ready")
        # insert to database
        from .Simulator_API import simulator_device_update
        simulator_device_update(None, get_value('client_ip'), data, device)


def dongle_error_callback(device='', code=0, message='', payload={}, timestamp=0, uuid='', **kwargs):
    msg = {
        'code': code,
        'message': message,
        'response': payload,
        'timestamp': timestamp,
        'uuid': uuid
    }
    data = pack_payload(msg)
    topic = get_value('mqtt_version') + "/simulator/devices/" + device + "/error"
    logger.info("Publish: topic:%s, %s", topic, data)
    if brokers and get_value('client_ip') in brokers:
        brokers[get_value('client_ip')].publish(topic, data, qos=2)
    else:
        logger.error("MQTT client is not ready")

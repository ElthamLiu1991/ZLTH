import base64
import json
import uuid

from zigbeeLauncher.mqtt import router
from zigbeeLauncher.mqtt.Callbacks import dongle_error_callback, simulator_error_callback, dongle_info_callback, \
    simulator_info_callback
from zigbeeLauncher.logging import simulatorLogger as logger
from zigbeeLauncher.dongle.Dongle import dongles
from zigbeeLauncher.util import pack_payload, except_handle


@router.route('/simulator/synchronized')
def synchronized(ip, payload):
    """
    发送simulator/info以及simulator/devices/*/info进行同步
    :return:
    """
    from zigbeeLauncher.mqtt.Simulator import Simulator
    simulator = Simulator()
    payload = json.loads(payload)
    target_ip = payload['data']['ip']
    data = pack_payload(simulator.get())
    from zigbeeLauncher.mqtt import mqtt_version
    topic = mqtt_version + "/"+target_ip+"/simulator/info"
    logger.info("Publish: topic:%s, payload:%s", topic, data)
    simulator.client.publish(topic, data, qos=2)


@router.route('/simulator')
def simulator(ip, payload):
    """
    获取Simulator以及Dongle设备详细信息，每个Dongle的信息单独发送
    :param client:
    :param payload:
    :return:
    """
    try:
        from zigbeeLauncher.mqtt.Simulator import Simulator
        simulator = Simulator()
        data = simulator.get()
        simulator_info_callback(data)
        pass
    except Exception as e:
        logger.exception("Error:%s", e)
    finally:
        pass


@router.route('/simulator/devices/+')
def simulator_device(ip, payload, device):
    """
    获取dongle设备详细信息
    :param client:
    :param payload:
    :param device:
    :return:
    """
    logger.info("Packing dongle '%s' info...", device)
    if device in dongles:
        data = dongles[device].property.get()
        dongle_info_callback(device, data)


@router.route('/simulator/command')
@except_handle(simulator_error_callback)
def simulator_command(ip='', payload=''):
    data = json.loads(payload)
    data_obj = data["data"]
    for key in data_obj.keys():
        command = key
        command_payload = data_obj[key]
        if command == "firmware" and command_payload:
            if "data" in command_payload:
                if "filename" in command_payload:
                    filename = command_payload["filename"]
                else:
                    filename = uuid.uuid1()
                # save data to file
                with open('./firmwares/' + filename, 'wb') as f:
                    f.write(base64.b64decode(command_payload["data"]))
            else:
                filename = command_payload["filename"]
            for device in command_payload["devices"]:
                if device in dongles:
                    dongle = dongles[device]
                    dongle.mqtt.add({
                        'timestamp': data['timestamp'],
                        'uuid': data['uuid'],
                        'data': {
                            'firmware': {
                                'filename': filename
                            }
                        }
                    })
            break
        elif command == 'label':
            label = command_payload['data']
            from zigbeeLauncher.mqtt.Simulator import Simulator
            simulator = Simulator()
            simulator.update(label=data['data']['label']['data'])
        elif command == 'config':
            for device in command_payload["devices"]:
                if device in dongles:
                    dongle = dongles[device]
                    dongle.mqtt.add(data)
        elif command == 'online':
            # simulation for online/offline change
            simulator = Simulator()
            simulator.update(connected=data_obj[command])
            for mac, dongle in dongles:
                dongle.property.update(connected=data_obj[command])

        else:
            logger.warn("unsupported command:%s", command)
            raise Exception("unsupported command: " + command)
    simulator_error_callback(timestamp=data['timestamp'], uuid=data['uuid'])


@router.route('/simulator/devices/+/command')
@except_handle(dongle_error_callback)
def simulator_device_command(ip="", payload="", device=""):
    data = json.loads(payload)
    if device in dongles:
        dongle = dongles[device]
        dongle.mqtt.add(data)



import base64

from zigbeeLauncher.mqtt import get_value
from zigbeeLauncher.mqtt.WiserZigbeeDongle import dongles_dict
from zigbeeLauncher.mqtt.WiserZigbeeGlobal import except_handle
from .WiserZigbeeDongleCommands import Command, send_command
from zigbeeLauncher.serial_protocol.SerialProtocolF0 import *
from zigbeeLauncher.serial_protocol.SerialProtocol01 import *
from zigbeeLauncher.serial_protocol.SerialProtocol02 import *
from .WiserZigbeeDongleUpgrade import *
from ..serial_protocol.SerialProtocol import error, timeout


def dongle_error_callback(device, msg):
    callback = get_value("dongle_error_callback")
    if callback:
        callback(device, msg)


def dongle_command_handle(device=None, timestamp=0, uuid="", data={}):
    if device not in dongles_dict:
        raise Exception("device not exist")
    dongle = dongles_dict[device]
    for key in data.keys():
        command = key
        payload = data[key]
        if dongles_dict[device].state == 2 and command != "reset" and command != "firmware":
            # cannot operate device when device in bootloader mode
            raise Exception("device is in bootloader mode")
        if command == "identify":
            send_command(Command(
                dongle=dongle,
                request=identify_request_handle,
                response=error,
                timeout=timeout), timestamp, uuid, None)
        elif command == "reset":
            if dongle.state == 2:
                # 在bootloader模式下reset需要先停止当前的transfer
                send_command(Command(
                    dongle=dongle,
                    request=bootloader_stop_transfer,
                    done=lambda: send_command(Command(
                        dongle=dongle,
                        request=bootloader_finish_transfer,
                        response=error,
                        timeout=timeout), timestamp, uuid, None),
                    response=error,
                    timeout=timeout,
                ), timestamp, uuid, None)
            else:
                send_command(Command(
                    dongle=dongle,
                    request=reset_request_handle,
                    response=error,
                    timeout=timeout), timestamp, uuid, None)

        elif command == "firmware":
            if "data" in payload:
                if "filename" in payload:
                    filename = payload["filename"]
                else:
                    filename = uuid.uuid1()
                filename = './firmwares/' + filename
                # save data to file
                with open(filename, 'wb') as f:
                    f.write(base64.b64decode(payload["data"]))
                file = WiserFile(filename)
                Upgrade(dongle, file)
            else:
                filename = './firmwares/' + payload['filename']
                file = WiserFile(filename)
                Upgrade(dongle, file)

        elif command == "label":
            send_command(Command(
                dongle=dongle,
                request=label_write_handle,
                done=lambda: send_command(Command(
                        dongle=dongles_dict[device],
                        request=label_request_handle,
                        timeout=timeout)),
                response=error,
                timeout=timeout,
            ), timestamp, uuid, payload["data"])
        elif command == "attribute":
            if 'value' in payload:
                send_command(Command(
                    dongle=dongle,
                    request=attribute_write_request_handle,
                    response=error,
                    timeout=timeout
                ), timestamp, uuid, payload)
            else:
                # retrieve attribute value
                send_command(Command(
                    dongle=dongle,
                    request=attribute_request_handle,
                    response=error,
                    timeout=timeout
                ), timestamp, uuid, payload)
        elif command == "join":
            send_command(Command(
                dongle=dongle,
                request=join_network_request_handle,
                response=error,
                timeout=timeout
            ), timestamp, uuid, payload)
        elif command == "leave":
            send_command(Command(
                dongle=dongle,
                request=leave_network_request_handle,
                response=error,
                timeout=timeout
            ), timestamp, uuid, None)
        elif command == "data_request":
            send_command(Command(
                dongle=dongle,
                request=data_request_handle,
                response=error,
                timeout=timeout
            ), timestamp, uuid, None)
        elif command == "config":
            # config command
            if 'endpoints' in payload:
                print("this is a config command")
            else:
                print("this is a get config command")
        else:
            raise Exception("unsupported command:"+command)

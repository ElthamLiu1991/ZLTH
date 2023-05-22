import base64
import json
import uuid
from dataclasses import asdict

from dacite import from_dict

from zigbeeLauncher.database.interface import DBDevice, DBSimulator, DBZigbee
from zigbeeLauncher.exceptions import DeviceNotFound, DeviceOffline, Unsupported, InvalidPayload
from zigbeeLauncher.logging import simulatorLogger as logger
from zigbeeLauncher.simulator.topic import Topic
from zigbeeLauncher.wait_response import add_response
from zigbeeLauncher.data_model import Sync, SimulatorInfo, DeviceInfo, CommandSimulator, CommandDevice, Message, \
    ErrorMessage
from zigbeeLauncher.util import Global

topic = Topic()
# Global.set(Global.SIMULATOR, topic)


def insert_simulator(simulator: SimulatorInfo):
    # insert simulator
    if simulator.simulator:
        DBSimulator(mac=simulator.simulator.mac).add(simulator.simulator)
    # insert device
    for device in simulator.devices:
        insert_device(device)


def insert_device(device: DeviceInfo):
    # insert device
    if device.device:
        DBDevice(mac=device.device.mac).add(device.device)
    # insert zigbee
    if device.zigbee:
        DBZigbee(mac=device.zigbee.mac).add(device.zigbee)


@topic.route('/<ip>/simulator/connected')
def handler_connected(message: Message, ip, sender):
    """
    simulator上线通知，收到该消息后应该发送/ip/simulator/sync, {'ip': get_current_ip()}获取simulator的信息
    :param message:
    :param ip: 发送方IP地址
    :return:
    """
    simulator = Global.get(Global.SIMULATOR)
    simulator.client.send_simulator_sync(ip)


@topic.route('/<ip>/simulator/sync')
def handler_sync(message: Message, ip, sender):
    """
    同步请求，收到该消息后应该发送/{发送方IP}/simulator/synced
    :param message: data_model.Message object
    :param ip: 本机IP地址
    :return:
    """
    sync = from_dict(data_class=Sync, data=message.data)
    simulator = Global.get(Global.SIMULATOR)
    simulator.client.send_simulator_synced(sync.ip, simulator.info)


@topic.route('/<ip>/simulator/synced')
def handler_synced(message: Message, ip, sender):
    """
    同步回复，收到该消息后应该更新本地对应的simulator和devices数据,
    同时，也发送自己的simulator数据给对方
    :param message: data_model.Message object
    :param ip: 本机的IP
    :return:
    """
    synced = from_dict(data_class=SimulatorInfo, data=message.data)
    insert_simulator(synced)
    if synced.ip != ip:
        simulator = Global.get(Global.SIMULATOR)
        simulator.client.send_simulator_received(synced.ip, simulator.info)


@topic.route('/<ip>/simulator/received')
def handler_synced(message: Message, ip, sender):
    """
    同步回复，收到该消息后应该更新本地对应的simulator和devices数据
    :param message: data_model.Message object
    :param ip: 本机的IP
    :return:
    """
    synced = from_dict(data_class=SimulatorInfo, data=message.data)
    insert_simulator(synced)



@topic.route('/<ip>/simulator/devices/<mac>/sync')
def handle_device_sync(message: Message, ip, mac, sender):
    """
    同步请求，收到该消息后应该发送/ip/simulator/devices/mac/synced
    :param message: data_model.Message object
    :param ip: 本机IP地址
    :param mac: 请求同步的MAC地址
    :return:
    """
    sync = from_dict(data_class=Sync, data=message.data)
    dongles = Global.get(Global.DONGLES)
    dongle = dongles.get(mac)
    if dongle:
        info = dongle.info
        simulator = Global.get(Global.SIMULATOR)
        simulator.client.send_device_synced(sync.ip, mac, info)
    else:
        raise DeviceNotFound(mac)


@topic.route('/<ip>/simulator/devices/<mac>/synced')
def handler_device_synced(message: Message, ip, mac, sender):
    """
    同步回复，收到该消息后应该更新本地devices数据
    :param message: data_model.Message object
    :param ip: 本机IP地址
    :param mac: 请求的MAC地址
    :return:
    """
    synced = from_dict(data_class=DeviceInfo, data=message.data)
    insert_device(synced)


@topic.route('/<ip>/simulator/info')
def handler_info(message: Message, ip, sender):
    """
    simulator info广播，与synced处理一致
    :param message: data_model.Message object
    :param ip: 发送方的IP地址
    :return:
    """
    handler_synced(message, ip)


@topic.route('/<ip>/simulator/devices/<mac>/info')
def handler_device_info(message: Message, ip, mac, sender):
    """
    device info广播，与synced处理一致
    :param message: data_model.Message object
    :param ip: 发送方IP地址
    :param mac: dongle MAC地址
    :return:
    """
    handler_device_synced(message, ip, mac, sender)


@topic.route('/<ip>/simulator/update')
def handler_update(message: Message, ip, sender):
    """
    simulator update广播，收到该消息应该更新本地simulator数据
    :param message: data_model.Message object
    :param ip: 发送方的IP地址
    :return:
    """
    for k, v in message.data.items():
        if k == 'connected':
            # update device also
            DBDevice(ip=ip).update({k: v})
        DBSimulator(ip=ip).update(message.data)


@topic.route('/<ip>/simulator/devices/<mac>/update')
def handler_device_update(message: Message, ip, mac, sender):
    """
    device update广播，收到该消息应该更新本地devices数据
    :param message: data_model.Message object
    :param ip: 发送方IP地址
    :param mac: dongle MAC地址
    :return:
    """
    for k, v in message.data.items():
        if k == 'zigbee':
            zigbee = from_dict(data_class=DBZigbee.DataModel, data=v)
            DBZigbee(mac=mac).update(asdict(zigbee))
        else:
            DBDevice(mac=mac).update({k: v})


@topic.route('/<ip>/simulator/error')
def handler_error(message: Message, ip, sender):
    """
    simulator错误通知，收到该消息后应该立即回复HTTP请求
    :param message: data_model.Message object
    :param ip:
    :return:
    """
    add_response(message.uuid, message)


@topic.route('/<ip>/simulator/command')
def handler_command(message: Message, ip, sender):
    """
    simulator命令处理
    :param message:
    :param ip: 本机IP地址
    :return:
    """
    simulator = Global.get(Global.SIMULATOR)
    dongles = Global.get(Global.DONGLES)
    try:
        command = from_dict(data_class=CommandSimulator, data=message.data)
    except Exception as e:
        logger.exception("simulator handle error")
        raise InvalidPayload(message.data)
    if command.label is not None:
        # label handle
        simulator.label = command.label.data
    elif command.firmware is not None:
        # firmware handle
        for mac in command.firmware.devices:
            dongle = dongles.get(mac)
            if not dongle:
                raise DeviceNotFound(mac)
            if not dongle.connected:
                raise DeviceOffline(mac)
            dongle.handle(message, sender)
    elif command.config is not None:
        # config handle
        message.data['config'] = command.config.config
        for mac in command.config.devices:
            dongle = dongles.get(mac)
            if not dongle:
                raise DeviceNotFound(mac)
            if not dongle.connected:
                raise DeviceOffline(mac)
            dongle.handle(message, sender)
    else:
        raise Unsupported(message.data)
    # add to response
    simulator.client.send_error(sender, ErrorMessage(
        code=0,
        message='',
        data={},
        timestamp=message.timestamp,
        uuid=message.uuid
    ))


@topic.route('/<ip>/simulator/devices/<mac>/command')
def handle_device_command(message: Message, ip, mac, sender):
    """
    device命令处理
    :param message: data_model.Message object
    :param ip: 本机IP地址
    :param mac: dongle MAC地址
    :return:
    """
    # command = from_dict(data_class=CommandDevice, data=message.payload)
    dongle = Global.get(Global.DONGLES).get(mac)
    if dongle:
        dongle.handle(message, sender)
    else:
        raise DeviceNotFound(mac)
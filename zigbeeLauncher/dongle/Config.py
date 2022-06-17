import threading
import time

import config

from zigbeeLauncher.serial_protocol.SerialProtocolF0 import *
from zigbeeLauncher.serial_protocol.SerialProtocol02 import *
from zigbeeLauncher.logging import dongleLogger as logger
from ..mqtt.Callbacks import dongle_error_callback


class SetConfig:
    """
    配置device
    """

    def __init__(self, dongle, payload, timestamp, uuid):
        self.dongle = dongle
        self.config = payload
        self.timestamp = timestamp
        self.uuid = uuid
        self.state = self.dongle.property.state
        self.start()

    def finish(self, **kwargs):
        """
        结束本次配置
        :return:
        """

        self.end()
        logger.info("set config finish:%s", self.dongle.property.mac)
        dongle_error_callback(**kwargs)

    def response(self, **kwargs):
        """
        判断命令是否正确处理，如果出现失败，停止本次配置
        :return:
        """
        if kwargs['code'] != 0:
            logger.error("set config failed, stop")
            self.finish(**kwargs)

    def start(self):
        """
        调用命令将设备进入等待配置模式
        :return:
        """
        logger.info('entering configure mode')
        self.dongle.property.boot = False
        command = self.dongle.request(
            timestamp=self.timestamp,
            uuid=self.uuid,
            response_cb=self.response,
            request_cb=configuration_state_change_request_handle
        )

        if not command.send('01').result():
            return
        self.write_node()
        # 需要等待device重启完毕

    def write_node(self):
        now = time.time()
        while not self.dongle.property.boot:
            if time.time() - now > 5:
                logger.error("dongle enter configured mode failed")
                dongle_error_callback(
                    device=self.dongle.property.mac,
                    code=5000,
                    message="dongle enter configured mode failed",
                    payload={},
                    timestamp=self.timestamp,
                    uuid=self.uuid
                )
                return
            time.sleep(0.1)
        self.dongle.property.update(state=9)    # update state to configuring mode
        logger.info('writing node')
        command = self.dongle.request(
            timestamp=self.timestamp,
            uuid=self.uuid,
            response_cb=self.response,
            request_cb=node_info_write_handle
        )

        if not command.send(self.config['node']).result():
            return
        self.write_endpoints()

    def write_endpoints(self):
        endpoints = self.config['endpoints']
        for endpoint in endpoints:
            logger.info('writing endpoint:%d', endpoint['id'])
            command = self.dongle.request(
                timestamp=self.timestamp,
                uuid=self.uuid,
                response_cb=self.response,
                request_cb=add_endpoint_handle
            )

            if not command.send(endpoint).result():
                return
        self.write_attributes()

    def write_attributes(self):
        def set(endpoint, cluster, server):
            payload = {
                'endpoint_id': endpoint,
                'cluster_id': cluster['id'],
                'server': server
            }
            if cluster['manufacturer']:
                payload['manufacturer_code'] = cluster['manufacturer_code']
            else:
                payload['manufacturer_code'] = 0

            count = 0
            while True:
                command = self.dongle.request(
                    timestamp=self.timestamp,
                    uuid=self.uuid,
                    response_cb=self.response,
                    request_cb=add_attributes_to_cluster_handle,
                )
                self.count = 0
                if count == 0:
                    attributes = cluster['attributes']
                else:
                    attributes = []
                    for index, attribute in enumerate(cluster['attributes']):
                        if index >= count:
                            attributes.append(attribute)
                payload['attributes'] = attributes
                if not command.send(payload, self).result():
                    return False
                count = count + self.count
                print("write count:{}, total:{}".format(count, len(cluster['attributes'])))
                if count == len(cluster['attributes']):
                    return True
                else:
                    print("write remain attributes")
                    continue

        endpoints = self.config['endpoints']
        for endpoint in endpoints:
            id = endpoint['id']
            for cluster in endpoint['server_clusters']:
                if len(cluster['attributes']) == 0:
                    continue
                if not set(id, cluster, True):
                    return
            for cluster in endpoint['client_clusters']:
                if len(cluster['attributes']) == 0:
                    continue
                if not set(id, cluster, False):
                    return
        self.write_commands()

    def write_commands(self):
        def set(endpoint, cluster, server):
            command = self.dongle.request(
                timestamp=self.timestamp,
                uuid=self.uuid,
                response_cb=self.response,
                request_cb=add_supported_command_to_cluster_handle
            )

            payload = {
                'endpoint_id': endpoint,
                'cluster_id': cluster['id'],
                'server': server
            }
            if cluster['manufacturer']:
                payload['manufacturer_code'] = cluster['manufacturer_code']
            else:
                payload['manufacturer_code'] = 0
            payload['commands'] = cluster['commands']

            if not command.send(payload).result():
                return False
            return True

        endpoints = self.config['endpoints']
        for endpoint in endpoints:
            id = endpoint['id']
            for cluster in endpoint['server_clusters']:
                if len(cluster['commands']['C->S']) == 0 and len(cluster['commands']['S->C']) == 0:
                    continue
                if not set(id, cluster, True):
                    return
            for cluster in endpoint['client_clusters']:
                if len(cluster['commands']['C->S']) == 0 and len(cluster['commands']['S->C']) == 0:
                    continue
                if not set(id, cluster, False):
                    return
        self.finish(
            device=self.dongle.property.mac,
            code=0,
            message="",
            payload={},
            timestamp=self.timestamp,
            uuid=self.uuid
        )

    def end(self):
        """
        调用命令将设备退出配置模式
        :return:
        """
        logger.info('exit configure mode')
        command = self.dongle.request(
            timestamp=self.timestamp,
            uuid=self.uuid,
            response_cb=self.response,
            request_cb=configuration_state_change_request_handle
        )

        if not command.send('02').result():
            return
        # update network state to default state
        self.dongle.property.update(state=1)
        self.dongle.property.update(zigbee=self.dongle.property.default()['zigbee'])


class GetConfig:
    """
    获取dongle config配置，包含node, endpoint, clusters, attributes, commands
    """

    def __init__(self, dongle, timestamp, uuid):
        self.dongle = dongle
        self.timestamp = timestamp
        self.uuid = uuid
        self.config = {}
        self.dongle.config = self

        self.start()

    def finish(self, **kwargs):
        """
        结束本次配置setting
        :return:
        """
        logger.info("get config finish:%s", self.dongle.property.mac)
        dongle_error_callback(**kwargs)

    def response(self, **kwargs):
        """
        判断命令是否正确处理，如果出现失败，停止本次配置
        :return:
        """
        if kwargs['code'] != 0:
            self.finish(**kwargs)
        else:
            # 设置config
            self.config.update(kwargs['payload'])

    def start(self):
        """
        获取设备node info
        :return:
        """
        logger.info('get node info')
        command = self.dongle.request(
            timestamp=self.timestamp,
            uuid=self.uuid,
            response_cb=self.response,
            request_cb=node_info_request_handle
        )

        if not command.send().result():
            return
        self.get_endpoints()

    def get_endpoints(self):
        """
        获取设备endpoint列表
        :return:
        """
        logger.info('get endpoint info')
        command = self.dongle.request(
            timestamp=self.timestamp,
            uuid=self.uuid,
            response_cb=self.response,
            request_cb=endpoint_list_request_handle
        )

        if not command.send().result():
            return
        self.get_clusters()

    def get_clusters(self):
        """
        获取设备cluster列表
        :return:
        """

        def response(**kwargs):
            if kwargs['code'] != 0:
                self.finish(**kwargs)
            else:
                data = kwargs['payload']
                for endpoint in self.config['endpoints']:
                    if endpoint['id'] == data['id']:
                        del data['id']
                        endpoint.update(data)
                        break
                print('current config:', self.config)

        logger.info('get clusters info')
        for endpoint in self.config['endpoints']:
            command = self.dongle.request(
                timestamp=self.timestamp,
                uuid=self.uuid,
                response_cb=response,
                request_cb=endpoint_descriptor_request_handle
            )

            if not command.send(endpoint['id']).result():
                return
        self.get_attributes()

    def get_attributes(self):
        """
        获取设备attribute列表
        处理逻辑：
        1. 调用attribute_list_request接口后，dongle会先返回status response，如果成功则继续处理
        2. 成功后dongle将会上报attribute_list_response(可能有多个），需要获取到该信息进行处理
        3. 当remains为0的时候，处理下一个cluster
        :return:
        """
        def get(endpoint, cluster, server):
            command = self.dongle.request(
                timestamp=self.timestamp,
                uuid=self.uuid,
                response_cb=self.response,
                request_cb=attribute_list_request_handle,
            )
            payload = {
                'endpoint_id': endpoint,
                'cluster_id': cluster['id'],
                'manufacturer': cluster['manufacturer'],
                'server': server
            }
            self.endpoint_id = endpoint
            self.cluster_id = cluster['id']
            self.manufacturer = cluster['manufacturer']
            self.manufacturer_code = 0
            self.server = server
            self.seq = 0

            if cluster['manufacturer']:
                payload['manufacturer_code'] = cluster['manufacturer_code']
                self.manufacturer_code = cluster['manufacturer_code']
            self.next = False  # set to True if get attribute response done

            self.retry_payload = payload
            if not command.send(payload).result():
                return False
            now = time.time()
            while True:
                if time.time() - now > 5:
                    # timeout
                    return False
                if self.next:
                    break
            return True

        logger.info('get attributes info')
        for endpoint in self.config['endpoints']:
            for cluster in endpoint['server_clusters']:
                self.cluster = cluster
                if not get(endpoint['id'], cluster, True):
                    return
            for cluster in endpoint['client_clusters']:
                self.cluster = cluster
                if not get(endpoint['id'], cluster, False):
                    return
        self.get_commands()

    def get_commands(self):
        """
        获取设备attribute列表
        处理逻辑：
        1. 调用attribute_list_request接口后，dongle会先返回status response，如果成功则继续处理
        2. 成功后dongle将会上报attribute_list_response(可能有多个），需要获取到该信息进行处理
        3. 当remains为0的时候，处理下一个cluster
        :return:
        """
        def response(payload={}, **kwargs):
            if kwargs['code'] != 0:
                # no commands in this cluster
                pass
            else:
                self.cluster['commands'].update(payload)

        def get(endpoint, cluster, server):
            command = self.dongle.request(
                timestamp=self.timestamp,
                uuid=self.uuid,
                response_cb=response,
                request_cb=supported_commands_list_request_handle
            )
            payload = {
                'endpoint_id': endpoint,
                'cluster_id': cluster['id'],
                'manufacturer': cluster['manufacturer'],
                'server': server
            }

            if cluster['manufacturer']:
                payload['manufacturer_code'] = cluster['manufacturer_code']
                self.manufacturer_code = cluster['manufacturer_code']

            if not command.send(payload).result():
                # don't handle this status for commands
                pass
            return True

        logger.info('get commands info')
        for endpoint in self.config['endpoints']:
            for cluster in endpoint['server_clusters']:
                self.cluster = cluster
                if not get(endpoint['id'], cluster, True):
                    return
            for cluster in endpoint['client_clusters']:
                self.cluster = cluster
                if not get(endpoint['id'], cluster, False):
                    return
        self.finish(
            device=self.dongle.property.mac,
            code=0,
            message="",
            payload={'config':self.config},
            timestamp=self.timestamp,
            uuid=self.uuid
        )
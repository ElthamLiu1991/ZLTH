import asyncio
import threading
import time

from zigbeeLauncher.data_model import ErrorMessage
from zigbeeLauncher.dongle.command import Request
from zigbeeLauncher.serial_protocol.serial_protocol_F0 import *
from zigbeeLauncher.serial_protocol.serial_protocol_02 import *
from zigbeeLauncher.logging import dongleLogger as logger
from zigbeeLauncher.serial_protocol.sp_02 import GetNodeInfo, GetEndpoints, GetEndpointDescriptor, GetAttributes
from zigbeeLauncher.tasks import Tasks


class SetConfig(Request):
    """
    配置device
    """

    def __init__(self, dongle, payload, timestamp, uuid):
        self.dongle = dongle
        self.config = payload
        self.timestamp = timestamp
        self.uuid = uuid
        self.state = self.dongle.property.state
        task = Tasks()
        task.add(self.start())

    def finish(self, **kwargs):
        """
        结束本次配置
        :return:
        """

        task = Tasks()
        task.add(self.end())
        logger.info("set config finish:%s", self.dongle.property.mac)
        dongle_error_callback(**kwargs)
        # update network state to default state
        self.dongle.property.update(state=1)
        self.dongle.property.update(zigbee=self.dongle.property.default()['zigbee'])

    def response(self, **kwargs):
        """
        判断命令是否正确处理，如果出现失败，停止本次配置
        :return:
        """
        if kwargs['code'] != 0:
            logger.error("set config failed, stop")
            self.finish(**kwargs)

    async def start(self):
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
        result = await command.send('01')
        if not result:
            return
        await self.write_node()
        # 需要等待device重启完毕

    async def write_node(self):
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
            await asyncio.sleep(0.01)
        self.dongle.property.update(state=9)  # update state to configuring mode
        logger.info('writing node')
        command = self.dongle.request(
            timestamp=self.timestamp,
            uuid=self.uuid,
            response_cb=self.response,
            request_cb=node_info_write_handle
        )
        result = await command.send(self.config['node'])
        if not result:
            return
        await self.write_endpoints()

    async def write_endpoints(self):
        endpoints = self.config['endpoints']
        for endpoint in endpoints:
            logger.info('writing endpoint:%d', endpoint['id'])
            command = self.dongle.request(
                timestamp=self.timestamp,
                uuid=self.uuid,
                response_cb=self.response,
                request_cb=add_endpoint_handle
            )
            result = await command.send(endpoint)
            if not result:
                return
        await self.write_attributes()

    async def write_attributes(self):
        async def set(endpoint, cluster, server):
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
                result = await command.send(payload, self)
                if not result:
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
                result = await set(id, cluster, True)
                if not result:
                    return
            for cluster in endpoint['client_clusters']:
                if len(cluster['attributes']) == 0:
                    continue
                result = await set(id, cluster, False)
                if not result:
                    return
        await self.write_commands()

    async def write_commands(self):
        async def set(endpoint, cluster, server):
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
            result = await command.send(payload)
            if not result:
                return False
            return True

        endpoints = self.config['endpoints']
        for endpoint in endpoints:
            id = endpoint['id']
            for cluster in endpoint['server_clusters']:
                if len(cluster['commands']['C->S']) == 0 and len(cluster['commands']['S->C']) == 0:
                    continue
                result = await set(id, cluster, True)
                if not result:
                    return
            for cluster in endpoint['client_clusters']:
                if len(cluster['commands']['C->S']) == 0 and len(cluster['commands']['S->C']) == 0:
                    continue
                result = await set(id, cluster, False)
                if not result:
                    return
        self.finish(
            device=self.dongle.property.mac,
            code=0,
            message="",
            payload={},
            timestamp=self.timestamp,
            uuid=self.uuid
        )

    async def end(self):
        """
        调用命令将设备退出配置模式
        :return:
        """
        logger.info('exit configure mode')
        command = self.dongle.request(
            timestamp=self.timestamp,
            uuid=self.uuid,
            request_cb=configuration_state_change_request_handle
        )
        result = await command.send('02')
        if not result:
            return


class GetConfig(Request):
    """
    获取dongle config配置，包含node, endpoint, clusters, attributes, commands
    """

    def __init__(self, dongle, message):
        self.dongle = dongle
        self.dongle.config = {}
        self.dongle.config_attributes = []
        self.dongle.config_attributes_done = False
        self.dongle.config_commands = []
        self.dongle.config_commands_done = False
        self.message = message
        self.config = {}
        self.endpoints = None
        self.retry = 5

        task = Tasks()
        task.add(self.start())

    def response(self, mac, uuid, timestamp, sp_response, sender):
        logger.info(f'response {mac}, {uuid}, {timestamp}, {sp_response}')
        # broadcast error if response.code is not 0

    def timeout(self, mac, sequence, uuid, timestamp):
        logger.warning(f'timeout {mac}, {sequence}, {uuid}, {timestamp}')

    def finish(self):
        """
        结束本次配置setting
        :return:
        """
        pass

    async def start(self):
        """
        获取设备node info
        :return:
        """

        def response(mac, uuid, timestamp, sp_response, sender):
            if sp_response.code != 0:
                self.dongle.send_error(sender, ErrorMessage(uuid=uuid,
                                                            timestamp=timestamp,
                                                            code=sp_response.code,
                                                            message=sp_response.message,
                                                            data=sp_response.data))
            else:
                self.dongle.config.update({'node': sp_response.data, 'endpoints':[]})

        logger.info('get node info')
        request = self.dongle.pack_request(
            message=self.message,
            request=GetNodeInfo(),
            response=response,
            timeout=self.timeout,
            retry=self.retry
        )

        await request.send()
        if request.result:
            await self.get_endpoints()

    async def get_endpoints(self):
        """
        获取设备endpoint列表
        :return:
        """
        def response(mac, uuid, timestamp, sp_response, sender):
            if sp_response.code != 0:
                self.dongle.send_error(sender, ErrorMessage(uuid=uuid,
                                                            timestamp=timestamp,
                                                            code=sp_response.code,
                                                            message=sp_response.message,
                                                            data=sp_response.data))
            else:
                self.endpoints = sp_response.data

        logger.info('get endpoint info')
        request = self.dongle.pack_request(
            message=self.message,
            request=GetEndpoints(),
            response=response,
            timeout=self.timeout,
            retry=self.retry
        )

        await request.send()
        if request.result:
            await self.get_clusters()

    async def get_clusters(self):
        """
        获取设备cluster列表
        :return:
        """
        def response(mac, uuid, timestamp, sp_response, sender):
            if sp_response.code != 0:
                self.dongle.send_error(sender, ErrorMessage(uuid=uuid,
                                                            timestamp=timestamp,
                                                            code=sp_response.code,
                                                            message=sp_response.message,
                                                            data=sp_response.data))
            else:
                self.dongle.config['endpoints'].append(sp_response.data)

        for endpoint in self.endpoints:
            logger.info(f'get endpoint:{endpoint} clusters info')
            request = self.dongle.pack_request(
                message=self.message,
                request=GetEndpointDescriptor(endpoint),
                response=response,
                timeout=self.timeout,
                retry=self.retry
            )
            await request.send()
            if not request.result:
                return
        await self.get_attributes()

    async def get_attributes(self):
        """
        获取设备attribute列表
        处理逻辑：
        1. 调用attribute_list_request接口后，dongle会先返回status response，如果成功则继续处理
        2. 成功后dongle将会上报attribute_list_response(可能有多个），需要获取到该信息进行处理
        3. 当remains为0的时候，处理下一个cluster
        :return:
        """
        def response(mac, uuid, timestamp, sp_response, sender):
            if sp_response.code != 0:
                self.dongle.send_error(sender, ErrorMessage(uuid=uuid,
                                                            timestamp=timestamp,
                                                            code=sp_response.code,
                                                            message=sp_response.message,
                                                            data=sp_response.data))

        for endpoint in self.config['endpoints']:
            for cluster in endpoint['server_clusters']:
                logger.info(f"get attributes endpoint:{endpoint['id']}, server cluster:{cluster['id']}")
                request = self.dongle.pack_request(
                    message=self.message,
                    request=GetAttributes(endpoint['id'], cluster['id'], cluster['manufacturer_code'], True),
                    response=response,
                    timeout=self.timeout,
                    retry=self.retry
                )
                await request.send()
                if not request.result:
                    return
                # wait attributes finish
                self.dongle.config_attributes_done = False
                while not self.dongle.config_attributes_done:
                    await asyncio.sleep(0.01)
                cluster['attributes'] = self.dongle.config_attributes
            for cluster in endpoint['client_clusters']:
                logger.info(f"get attributes endpoint:{endpoint['id']}, client cluster:{cluster['id']}")
                request = self.dongle.pack_request(
                    message=self.message,
                    request=GetAttributes(endpoint['id'], cluster['id'], cluster['manufacturer_code'], False),
                    response=response,
                    timeout=self.timeout,
                    retry=self.retry
                )
                await request.send()
                if not request.result:
                    return
                # wait attributes finish
                self.dongle.config_attributes_done = False
                while not self.dongle.config_attributes_done:
                    await asyncio.sleep(0.01)
                cluster['attributes'] = self.dongle.config_attributes
        await self.get_commands()

    async def get_commands(self):
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

        async def get(endpoint, cluster, server):
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
            result = await command.send(payload)
            if not result:
                # don't handle this status for commands
                pass
            return True

        logger.info('get commands info')
        for endpoint in self.config['endpoints']:
            for cluster in endpoint['server_clusters']:
                self.cluster = cluster
                result = await get(endpoint['id'], cluster, True)
                if not result:
                    return
            for cluster in endpoint['client_clusters']:
                self.cluster = cluster
                result = await get(endpoint['id'], cluster, False)
                if not result:
                    return
        self.finish(
            device=self.dongle.property.mac,
            code=0,
            message="",
            payload={'config': self.config},
            timestamp=self.timestamp,
            uuid=self.uuid
        )

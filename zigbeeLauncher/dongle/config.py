import asyncio
import threading
import time

from zigbeeLauncher.data_model import ErrorMessage, Config
from zigbeeLauncher.dongle.command import Request
from zigbeeLauncher.dongle.info import Info
from zigbeeLauncher.logging import dongleLogger as logger
from zigbeeLauncher.serial_protocol.sp_02 import GetNodeInfo, GetEndpoints, GetEndpointDescriptor, GetAttributes, \
    GetCommands, WriteNodeInfo, AddEndpoint, Cluster, AddAttributes, SPAttribute, SPAttributeWrite, AddCommands, \
    SPCommand
from zigbeeLauncher.serial_protocol.sp_f0 import SetConfiguration
from zigbeeLauncher.tasks import Tasks


class SetConfig(Request):
    """
    配置device
    """

    def __init__(self, dongle, message, config: Config):
        self.dongle = dongle
        self.message = message
        self.config = config

        self.running = True
        self.retry = 5
        task = Tasks()
        task.add(self.start())

    def response(self, mac, uuid, timestamp, sp_response, sender):
        logger.info(f'response {mac}, {uuid}, {timestamp}, {sp_response}')
        # broadcast error if response.code is not 0
        if sp_response.code != 0 and self.running:
            task = Tasks()
            task.add(self.stop())
            self.dongle.send_error(sender, ErrorMessage(uuid=uuid,
                                                        timestamp=timestamp,
                                                        code=sp_response.code,
                                                        message=sp_response.message,
                                                        data=sp_response.data))
            self.running = False

    def timeout(self, mac, sequence, uuid, timestamp):
        logger.warning(f'timeout {mac}, {sequence}, {uuid}, {timestamp}')
        task = Tasks()
        task.add(self.stop())

    def finish(self):
        """
        结束本次配置，重新获取info信息
        :return:
        """

        Info(self.dongle)

    async def start(self):
        """
        调用命令将设备进入等待配置模式
        :return:
        """
        logger.info('entering configure mode')
        self.dongle.boot = False
        request = self.dongle.pack_request(
            message=self.message,
            request=SetConfiguration(False),
            response=self.response,
            timeout=self.timeout,
            retry=self.retry
        )
        await request.send()
        if request.result:
            await self.set_node()

    async def set_node(self):
        while not self.dongle.boot:
            await asyncio.sleep(1)
        # self.dongle.state = self.dongle.DongleMetaData.CONFIGURING
        node = self.config.node
        request = self.dongle.pack_request(
            message=self.message,
            request=WriteNodeInfo(node.device_type, node.radio_power, node.manufacturer_code),
            response=self.response,
            timeout=self.timeout,
            retry=self.retry
        )
        await request.send()
        if request.result:
            await self.set_endpoints()

    async def set_endpoints(self):
        endpoints = self.config.endpoints
        for endpoint in endpoints:
            logger.info(f'writing endpoint:{endpoint.id}')
            server_clusters = []
            client_clusters = []
            for cluster in endpoint.server_clusters:
                server_clusters.append(Cluster(
                    cluster=cluster.id,
                    manufacturer_code=0 if not cluster.manufacturer else cluster.manufacturer_code
                ))
            for cluster in endpoint.client_clusters:
                client_clusters.append(Cluster(
                    cluster=cluster.id,
                    manufacturer_code=0 if not cluster.manufacturer else cluster.manufacturer_code
                ))
            request = self.dongle.pack_request(
                message=self.message,
                request=AddEndpoint(
                    endpoint=endpoint.id,
                    profile=endpoint.profile_id,
                    device=endpoint.device_id,
                    version=endpoint.device_version,
                    servers=server_clusters,
                    clients=client_clusters
                ),
                response=self.response,
                timeout=self.timeout,
                retry=self.retry
            )
            await request.send()
            if not request.result:
                return
        await self.set_attributes()

    async def set_attributes(self):
        async def _set_attributes(endpoint, cluster, server, attributes):
            while attributes:
                request = self.dongle.pack_request(
                    message=self.message,
                    request=AddAttributes(
                        endpoint=endpoint.id,
                        cluster=cluster.id,
                        manufacturer_code=cluster.manufacturer_code if cluster.manufacturer else 0,
                        server=server,
                        attributes=attributes
                    ),
                    response=self.response,
                    timeout=self.timeout,
                    retry=self.retry
                )
                await request.send()
                if not request.result:
                    return False
            return True

        endpoints = self.config.endpoints
        for endpoint in endpoints:
            for cluster in endpoint.server_clusters:
                logger.info(f"set attributes for {endpoint.id}, {cluster.id}")
                attributes = []
                for attribute in cluster.attributes:
                    attributes.append(SPAttributeWrite(
                        attribute=attribute.id,
                        manufacturer_code=attribute.manufacturer_code if attribute.manufacturer else 0,
                        type=attribute.type,
                        writable=attribute.writable,
                        length=attribute.length if attribute.length else 0,
                        default=attribute.default
                    ))
                if not await _set_attributes(endpoint, cluster, True, attributes):
                    return
            for cluster in endpoint.client_clusters:
                attributes = []
                for attribute in cluster.attributes:
                    attributes.append(SPAttributeWrite(
                        attribute=attribute.id,
                        manufacturer_code=attribute.manufacturer_code if attribute.manufacturer else 0,
                        type=attribute.type,
                        writable=attribute.writable,
                        length=attribute.length if attribute.length else 0,
                        default=attribute.default
                    ))
                if not await _set_attributes(endpoint, cluster, False, attributes):
                    return
        await self.set_commands()

    async def set_commands(self):
        async def _set_commands(endpoint, cluster, server, commands):
            print("_set_commands:", endpoint.id, cluster.id, server, commands)
            request = self.dongle.pack_request(
                message=self.message,
                request=AddCommands(
                    endpoint=endpoint.id,
                    cluster=cluster.id,
                    manufacturer_code=cluster.manufacturer_code if cluster.manufacturer else 0,
                    server=server,
                    commands=commands
                ),
                response=self.response,
                timeout=self.timeout,
                retry=self.retry
            )
            print("request:", request)
            await request.send()
            if not request.result:
                return False
            return True

        endpoints = self.config.endpoints
        for endpoint in endpoints:
            for cluster in endpoint.server_clusters:
                logger.info(f"server, set server command:{endpoint.id}, {cluster.id}, {cluster.server_commands}")
                commands = []
                for command in cluster.server_commands:
                    print(f"server command:", command)
                    commands.append(SPCommand(
                        command=command.id,
                        mask=1,
                        manufacturer_code=command.manufacturer_code if command.manufacturer else 0,

                    ))
                print("commands:", commands)
                if commands:
                    if not await _set_commands(endpoint, cluster, True, commands):
                        print("set command failed")
                        return
                logger.info(f"server, set client command:{endpoint.id}, {cluster.id}, {cluster.client_commands}")
                commands = []
                for command in cluster.client_commands:
                    commands.append(SPCommand(
                        command=command.id,
                        mask=0,
                        manufacturer_code=command.manufacturer_code if command.manufacturer else 0,

                    ))
                print("commands:", commands)
                if commands:
                    if not await _set_commands(endpoint, cluster, True, commands):
                        print("set command failed")
                        return
            for cluster in endpoint.client_clusters:
                logger.info(f"client, set server command:{endpoint.id}, {cluster.id}, {cluster.server_commands}")
                commands = []
                for command in cluster.server_commands:
                    commands.append(SPCommand(
                        command=command.id,
                        mask=1,
                        manufacturer_code=command.manufacturer_code if command.manufacturer else 0,

                    ))
                print("commands:", commands)
                if commands:
                    if not await _set_commands(endpoint, cluster, False, commands):
                        print("set command failed")
                        return
                logger.info(f"client, set client command:{endpoint.id}, {cluster.id}, {cluster.client_commands}")
                commands = []
                for command in cluster.client_commands:
                    commands.append(SPCommand(
                        command=command.id,
                        mask=0,
                        manufacturer_code=command.manufacturer_code if command.manufacturer else 0,

                    ))
                print("commands:", commands)
                if commands:
                    if not await _set_commands(endpoint, cluster, False, commands):
                        print("set command failed")
                        return
        await self.stop()

    async def stop(self):
        """
        调用命令将设备退出配置模式
        :return:
        """
        logger.info('exit configure mode')
        self.dongle.boot = False
        request = self.dongle.pack_request(
            message=self.message,
            request=SetConfiguration(True),
            response=self.response,
            timeout=self.timeout,
            retry=self.retry
        )
        await request.send()
        if request.result:
            Info(self.dongle)


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
        self.dongle.send_error(self.dongle._sender, ErrorMessage(uuid=self.message.uuid,
                                                                 timestamp=self.message.timestamp,
                                                                 code=0,
                                                                 message="",
                                                                 data={'config': self.dongle.config}))

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
                self.dongle.config.update({'node': sp_response.data, 'endpoints': []})

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
        if not request.result:
            return
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
        async def _get_attributes(endpoint, cluster, server):
            def _response(mac, uuid, timestamp, sp_response, sender):
                if sp_response.code != 0:
                    self.dongle.send_error(sender, ErrorMessage(uuid=uuid,
                                                                timestamp=timestamp,
                                                                code=sp_response.code,
                                                                message=sp_response.message,
                                                                data=sp_response.data))

            request = self.dongle.pack_request(
                message=self.message,
                request=GetAttributes(endpoint, cluster['id'], cluster['manufacturer_code'], server),
                response=_response,
                timeout=self.timeout,
                retry=self.retry
            )
            await request.send()
            if not request.result:
                return False
            # wait attributes finish
            while not self.dongle.config_attributes_done:
                await asyncio.sleep(0.01)
            cluster['attributes'] = self.dongle.config_attributes.copy()
            print('attributes', cluster['attributes'])
            self.dongle.config_attributes = []
            self.dongle.config_attributes_done = False
            return True

        for endpoint in self.dongle.config['endpoints']:
            for cluster in endpoint['server_clusters']:
                logger.info(f"get attributes endpoint:{endpoint['id']}, server cluster:{cluster['id']}")
                if not await _get_attributes(endpoint['id'], cluster, True):
                    return
            for cluster in endpoint['client_clusters']:
                logger.info(f"get attributes endpoint:{endpoint['id']}, client cluster:{cluster['id']}")
                if not await _get_attributes(endpoint['id'], cluster, False):
                    return
        await self.get_commands()

    async def get_commands(self):
        async def _get_commands(endpoint, cluster, server):
            def _response(mac, uuid, timestamp, sp_response, sender):
                pass

            request = self.dongle.pack_request(
                message=self.message,
                request=GetCommands(endpoint, cluster['id'], cluster['manufacturer_code'], server),
                response=_response,
                timeout=self.timeout,
                retry=self.retry
            )
            await request.send()
            # if not request.result:
            #     return False
            if server:
                cluster['commands']['S->C'] = self.dongle.config_commands.copy()
            else:
                cluster['commands']['C->S'] = self.dongle.config_commands.copy()

            self.dongle.config_commands = []
            return True

        for endpoint in self.dongle.config['endpoints']:
            for cluster in endpoint['server_clusters']:
                logger.info(f"get commands endpoint:{endpoint['id']}, server cluster:{cluster['id']}")
                if not await _get_commands(endpoint['id'], cluster, True):
                    return
            for cluster in endpoint['client_clusters']:
                logger.info(f"get commands endpoint:{endpoint['id']}, client cluster:{cluster['id']}")
                if not await _get_commands(endpoint['id'], cluster, False):
                    return
        # pack response
        self.finish()

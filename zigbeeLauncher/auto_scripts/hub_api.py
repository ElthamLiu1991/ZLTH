import os.path
import shutil
import time

import paramiko
from scp import SCPClient

from zigbeeLauncher.auto_scripts.wiser_api import WiserAPI, WiserMQTT
from zigbeeLauncher.logging import autoLogger as logger


class HubAPI:
    HUB_PATH = './hub'
    HUB_WSE_DB_FILE = './wse.db'
    HUB_WDC_DB_FILE = './device.db'
    HUB_LOG_PATH = '/tmp/.run_apps/log'

    def __init__(self, record, host, tuya, username='fio', port=22, password='fio'):
        self.ip = host
        self.port = port
        self.username = username
        self.password = password
        self.connection = None
        self.folder = f'{self.HUB_PATH}/{record}'
        self.tuya = tuya
        self.files = ''
        self._stop = False
        self._connect()

    def _connect(self):
        self.connection = paramiko.SSHClient()
        self.connection.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            if self.password != '':
                self.connection.connect(self.ip, self.port, self.username, (str(self.password)), timeout=5.0)
            else:
                try:
                    self.connection.connect(self.ip, self.port, self.username, look_for_keys=False,
                                            allow_agent=False, timeout=5.0)
                except paramiko.ssh_exception.SSHException:
                    self.connection.get_transport().auth_none(self.username)
                    self.connection.exec_command('uname -a')
                self.connection.sftp = paramiko.SFTPClient.from_transport(self.connection.get_transport())
        except Exception as e:
            try:
                logger.info(str(e.args))
                self.connection = None
            finally:
                e = None
                del e

    def _get_file(self, file):
        if self.connection:
            with SCPClient(self.connection.get_transport()) as scp:
                scp.get(file, f'{self.files}/', recursive=True)

    def connect(self):
        timestamp = int(time.time())
        while int(time.time()) - timestamp < 120:
            if self._stop:
                return False
            self._connect()
            if self.connection:
                logger.info(f"hub {self.ip} connected")
                return True
        logger.error(f"hub {self.ip} connected timeout")
        return False

    def get_hub_files(self):
        if os.path.exists(self.files):
            shutil.rmtree(self.files)
        os.makedirs(self.files)
        # copy database from container to host
        stdin, stdout, stderr = self.connection.exec_command('docker cp wse:/wiser/data/db/wse.db .')
        logger.info(stdout.read())
        stdin, stdout, stderr = self.connection.exec_command('docker cp wdc:/wiser/data/db/device.db .')
        logger.info(stdout.read())
        # get database
        self._get_file(self.HUB_WSE_DB_FILE)
        self._get_file(self.HUB_WDC_DB_FILE)
        self._get_file(self.HUB_LOG_PATH)
        # delete database
        stdin, stdout, stderr = self.connection.exec_command(f'rm {self.HUB_WSE_DB_FILE}')
        logger.info(stdout.read())
        stdin, stdout, stderr = self.connection.exec_command(f'rm {self.HUB_WDC_DB_FILE}')
        logger.info(stdout.read())
        logger.info("get hub files done, reboot hub")
        self.reboot()

    def set_folder(self, path=None):
        """
        :param path:
        :return:
        """
        self.files = f'{self.folder}/{path}' if path else self.folder

    def reboot(self):
        stdin, stdout, stderr = self.connection.exec_command(f'echo "fio" | sudo -S reboot')
        logger.info(stdout.read())
        self.connection.close()
        self.connection = None
        time.sleep(5)
        # timestamp = int(time.time())
        # while int(time.time()) - timestamp < 120:
        #     if self._stop:
        #         break
        timestamp = int(time.time())
        while not self.tuya.is_online() and int(time.time()) - timestamp < 300:
            if self._stop:
                break
            time.sleep(5)

        # logger.info("Waiting hub reboot")
        # wiser = WiserMQTT(self.ip)
        # wiser.start()
        # timestamp = int(time.time())
        # while True:
        #     if self._stop:
        #         break
        #     if int(time.time()) - timestamp > 300:
        #         logger.warning("reboot timeout")
        #         break
        #     if wiser.connected:
        #         break
        #     time.sleep(5)
        # if not wiser.connected:
        #     logger.warning("Connect hub failed")
        # else:
        #     timestamp = int(time.time())
        #     logger.info("Hub reboot success, wait container ready")
        #     while True:
        #         if self._stop:
        #             break
        #         if int(time.time()) - timestamp > 60:
        #             logger.warning("containers initial timeout")
        #             break
        #         if wiser.wiser_api.get_network():
        #             break
        #         time.sleep(5)
        #     if wiser.wiser_api.get_network():
        #         timestamp = int(time.time())
        #         while True:
        #             if self._stop:
        #                 break
        #             if int(time.time()) - timestamp > 300:
        #                 break
        # logger.info("container initial done")
        # wiser.stop()
        # del wiser

    def is_connected(self):
        return True if self.connection else False

    def stop(self):
        self._stop = True

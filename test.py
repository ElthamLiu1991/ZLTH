import os.path
import platform
import shutil
import time

import paramiko
from scp import SCPClient

from zigbeeLauncher.logging import autoLogger as logger

class HubSSH:
    HUB_PATH = './hub'
    HUB_WSE_DB_FILE = '/wse.db'
    HUB_WDC_DB_FILE = '/device.db'
    HUB_LOG_PATH = '/tmp/.run_apps/log'

    def __init__(self, host='192.168.121.35', username='fio', port=22, password='fio'):
        self.ip = host
        self.port = port
        self.username = username
        self.password = password
        self.connection = None
        self.folder = self.HUB_PATH
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
                scp.get(file, f'{self.folder}/', recursive=True)

    def get_hub_files(self):
        if os.path.exists(self.folder):
            shutil.rmtree(self.folder)
        os.mkdirs(self.folder)
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
        logger.info(stdout.read(), stderr.read())
        stdin, stdout, stderr = self.connection.exec_command(f'rm {self.HUB_WDC_DB_FILE}')
        logger.info(stdout.read(), stderr.read())
        logger.info("get hub files done, reboot hub")
        self.hub_reboot()

    def set_folder(self, folder):
        """
        :param folder: can be multiple layer, capacity-xxx/repeat-1 or compose-xxx/capacity/repeat-1
        :return:
        """
        self.folder += folder

    def hub_reboot(self):
        stdin, stdout, stderr = self.connection.exec_command(f'echo "fio" | sudo -S reboot')
        logger.info(stdout.read(), stderr.read())
        self.connection.close()
        time.sleep(5*60)
        logger.info("hub is online")


if __name__ == '__main__':
    hub = HubSSH()
    if hub.connection:
        hub.get_hub_files('test')
        hub.hub_reboot()

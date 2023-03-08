import os

from flask import render_template, make_response
from flask_restful import Resource
from zigbeeLauncher.api_2.autos import scripts
from zigbeeLauncher.database.interface import DBAuto
from zigbeeLauncher.exceptions import exception, Unsupported, NotFound, ConfigInvalid, ScriptRunning, ScriptNotReady
from zigbeeLauncher.logging import flaskLogger as logger
from zigbeeLauncher.auto_scripts import AutoTesting, State, Result, Error


class AutoResource(Resource):
    """
    /auto
    """

    def get(self):
        """
        获取内置自动化脚本列表
        :return:
        """
        @exception
        def handle():
            return scripts
        return handle()


class AutoOperationResource(Resource):
    """
    /auto/<operation>
    """
    operations = ['running', 'history', 'records']

    def get(self, operation):
        """
        running: 获取正在运行的列表
        history: 获取以及结束的列表
        records: 获取所有的列表
        :param operation:
        :return:
        """
        records = []
        if operation == 'running':
            for record in DBAuto().retrieve():
                if record['state'] != State.FINISH:
                    records.append(record)
        elif operation == 'history':
            records = DBAuto().retrieve()
            for item in records:
                if item['state'] == State.FINISH:
                    records.remove(item)
        elif operation == 'records':
            records = DBAuto().retrieve()
        data = {}
        for record in records:
            if record['state'] != State.FINISH:
                data[record['record']] = record['state']
            else:
                data[record['record']] = record['result']
        html = render_template('records.html', records=data)

        return make_response(html)
        # return Response(data=records).pack()


class AutoOperationRecordsResource(Resource):
    """
    /auto/records/<record>
    """
    def get(self, record):
        html = render_template('autos.html', current_script=record)

        return make_response(html)


class AutoScriptsResource(Resource):

    def get(self, script):
        """
        返回内置脚本template
        :param script:
        :return:
        """
        record = AutoTesting().set_script(script)
        html = render_template('autos.html', current_script=record)
        return make_response(html)

    def post(self, script):
        """
        触发内置自动化脚本
        :return:
        """
        @exception
        def handle():
            if script not in scripts:
                raise Unsupported(script)
            logger.info(f'triggering script:{script}')
            record = AutoTesting().set_script(script)
            if record:
                result = AutoTesting().start(record)
                if result == Error.NO_ERROR:
                    return {'record': record}
                elif result == Error.RUNNING:
                    raise ScriptRunning(script)
                elif result == Error.INVALID_CONFIG:
                    raise ConfigInvalid(script)
                elif result == Error.NOT_FOUND:
                    raise NotFound(script)
            else:
                raise ScriptNotReady(script)

        return handle()


class AutoScriptsConfigResource(Resource):

    def get(self, script):
        """
        获取内置自动化脚本列表配置信息
        :return:
        """
        pass

    def put(self, script):
        """
        修改内置自动化脚本配置信息
        :param script:
        :return:
        """
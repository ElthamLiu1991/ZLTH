import os

from flask import render_template, make_response
from flask_restful import Resource

from zigbeeLauncher import base_dir
from zigbeeLauncher.api_2.autos import scripts
from zigbeeLauncher.database.interface import DBAuto
from zigbeeLauncher.logging import flaskLogger as logger
from zigbeeLauncher.api_2.response import Response
from zigbeeLauncher.auto_scripts import AutoTesting, WORKING, FINISH


class AutoResource(Resource):

    def get(self):
        """
        获取内置自动化脚本列表
        :return:
        """
        return Response(data=scripts).pack()


class AutoOperationResource(Resource):
    operations = ['running', 'history', 'records']

    def get(self, operation):
        """
        running: 获取正在允许的列表
        history: 获取以及结束的列表
        records: 获取所有的列表
        :param operation:
        :return:
        """
        records = []
        if operation not in self.operations:
            return Response(operation, code=70002).pack()
        if operation == 'running':
            for record in DBAuto().retrieve():
                if record['state'] != FINISH:
                    records.append(record)
        elif operation == 'history':
            records = DBAuto(state=FINISH).retrieve()
        elif operation == 'records':
            records = DBAuto().retrieve()
        data = {}
        for record in records:
            data[record['record']] = record['status']
        html = render_template('records.html', records=data)

        return make_response(html)
        # return Response(data=records).pack()


class AutoOperationRecordsResource(Resource):

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
        if script not in scripts:
            return Response(script, code=70000).pack()
        record = AutoTesting().set_script(script)
        html = render_template('autos.html', current_script=record)
        return make_response(html)

    def post(self, script):
        """
        触发内置自动化脚本
        :return:
        """
        if script not in scripts:
            return Response(script, code=70000).pack()
        logger.info('triggering script:%s', script)
        # 进入auto_scripts加载对应的script, 返回record的文件名称，并保持到数据库中
        record = AutoTesting().set_script(script)
        if record:
            AutoTesting().start(record)
            return Response(data={'record': record}).pack()
        else:
            return Response(script, code=70001).pack()


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
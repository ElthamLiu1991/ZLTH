import os

from flask import render_template, make_response
from flask_restful import Resource

from zigbeeLauncher import base_dir
from zigbeeLauncher.api_2.autos import scripts
from zigbeeLauncher.logging import flaskLogger as logger
from zigbeeLauncher.api_2.response import Response
from zigbeeLauncher.auto_scripts import AutoTesting


class AutoResource(Resource):

    def get(self):
        """
        获取内置自动化脚本列表
        :return:
        """
        result = []
        for item in scripts:
            script = {'script': item, 'state': 'ready'}
            running_script = AutoTesting(item).name()
            if running_script and running_script == item:
                script['state'] = 'running'
            result.append(script)
        return Response(data=result).pack()


class AutoScriptResource(Resource):

    def get(self, script):
        """
        返回内置脚本template
        :param script:
        :return:
        """
        if script not in scripts:
            return Response(script, code=70000).pack()
        html = render_template('autos.html')
        AutoTesting().set_script(script)

        return make_response(html)

    def post(self, script):
        """
        触发内置自动化脚本
        :return:
        """
        if script not in scripts:
            return Response(script, code=70000).pack()
        logger.info('triggering script:%s', script)
        # 进入auto_scripts加载对应的script
        testing = AutoTesting()
        testing.set_script(script)
        if testing.is_ready():
            testing.run()
            return Response().pack()
        else:
            return Response(script, code=70001).pack()


class AutoConfigResource(Resource):

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
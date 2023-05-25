from flask_restful import Resource

from zigbeeLauncher.exceptions import exception


class LogsResource(Resource):
    """
    /logs
    """

    def get(self):
        @exception
        def handle():
            log = f'./logs/info.log'
            data=""
            with open(log, 'r', encoding='utf-8') as f:
                data = f.readlines()
            return data

        return handle()

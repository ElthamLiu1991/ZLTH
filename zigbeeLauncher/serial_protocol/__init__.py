#from zigbeeLauncher.util import Response


class Response(object):
    """
    保存串口response消息ID与schema和callback的映射
    自动调用callback
    """
    def __init__(self):
        self.url_map = {}

    def cmd(self, url, schema={}):
        def wrapper(func):
            self.url_map[url] = (schema, func)
        return wrapper

    def get_schema(self, url):
        schema = self.url_map.get(url)
        if not schema:
            raise ValueError('No serial schema for this command')
        else:
            return schema

    def call(self, url, instance):
        func = self.url_map.get(url)
        if not func:
            raise ValueError('No response function: %s', url)
        else:
            return func(instance)

response = Response()
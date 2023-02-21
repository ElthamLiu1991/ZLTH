import json
import re

from dacite import from_dict

from zigbeeLauncher.data_model import Message, ErrorMessage
from zigbeeLauncher.exceptions import InvalidPayload, Unsupported, DeviceNotFound, DeviceOffline
from zigbeeLauncher.logging import mqttLogger as logger
from zigbeeLauncher.util import Global


class Topic:

    def __init__(self):
        self.routers = []

    @staticmethod
    def build_router_re(route):
        route_regex = re.sub('(<\w+>)', r'(?P\1.+)', route)
        route_reg_str = "^{}$".format(route_regex)
        return re.compile(route_reg_str)

    def route(self, routh_str):
        def decorator(f):
            logger.info(f'register MQTT router:{routh_str}')
            route_pattern = self.build_router_re(routh_str)
            self.routers.append((route_pattern, f))
            return f
        return decorator

    def get_match_route(self, path):
        for pattern, view_func in self.routers:
            m = pattern.match(path)
            if m:
                return m.groupdict(), view_func

    def run(self, path, payload, sender):
        # check payload is valid MQTT message format
        simulator = Global.get(Global.SIMULATOR)
        try:
            payload = json.loads(payload)
            message = from_dict(data_class=Message, data=payload)
        except Exception as e:
            logger.exception('invalid payload')
            return
        try:
            route_match = self.get_match_route(path)
            if route_match:
                if simulator.client.ip == simulator.client.broker:
                    if '/info' in path or '/update' in path or '/error' in path:
                        # forward to web client
                        simulator.client.forward(path, payload)
                kwargs, view_function = route_match
                kwargs['sender'] = sender
                return view_function(message, **kwargs)
            else:
                raise Unsupported(path)
        except DeviceNotFound as e:
            e.uuid = message.uuid
            e.timestamp = message.timestamp
            simulator.client.send_error(sender, e.error)
        except DeviceOffline as e:
            e.uuid = message.uuid
            e.timestamp = message.timestamp
            simulator.client.send_error(sender, e.error)
        except InvalidPayload as e:
            e.uuid = message.uuid
            e.timestamp = message.timestamp
            simulator.client.send_error(sender, e.error)
        except Unsupported as e:
            e.uuid = message.uuid
            e.timestamp = message.timestamp
            simulator.client.send_error(sender, e.error)
        except Exception as e:
            logger.exception("mqtt message handle error:")
            e = ErrorMessage(code=200, message='internal error', data={}, uuid=message.uuid, timestamp=message.timestamp)
            simulator.client.send_error(sender, e)



import time
import uuid
from dataclasses import dataclass, asdict
from functools import wraps
from typing import Any

from zigbeeLauncher.data_model import ErrorMessage, Message
from zigbeeLauncher.logging import errorLogger as logger


def exception(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        response = RequestException(0, "")
        try:
            data = func(*args, **kwargs)
            print(f"func return:{data}")
            if isinstance(data, Message):
                response.error = data
            else:
                response.data = data
        except InvalidRequest as e:
            response = e
            logger.exception("error:")
        except DeviceNotFound as e:
            response = e
            logger.exception("error:")
        except DeviceOffline as e:
            response = e
            logger.exception("error:")
        except DeviceNotReady as e:
            response = e
            logger.exception("error:")
        except Unreachable as e:
            response = e
            logger.exception("error:")
        except InvalidPayload as e:
            response = e
            logger.exception("error:")
        except Unsupported as e:
            response = e
            logger.exception("error:")
        except NotFound as e:
            response = e
            logger.exception("error:")
        except OutOfRange as e:
            response = e
            logger.exception("error:")
        except Timeout as e:
            response = e
            logger.exception("error:")
        except ConfigInvalid as e:
            response = e
            logger.exception("error:")
        except ScriptNotReady as e:
            response = e
            logger.exception("error:")
        except ScriptRunning as e:
            response = e
            logger.exception("error:")
        except Exception as e:
            response = RequestException(200, 'internal error')
            logger.exception("error:")
        finally:
            return asdict(response.error)
    return wrapper


class RequestException(Exception):

    _DeviceNotFound = 101
    _DeviceOffline = 102
    _DeviceNotReady = 103
    _Unreachable = 104

    _InvalidPayload = 105

    _Unsupported = 106
    _NotFound = 107
    _OutOfRange = 108

    _Timeout = 109

    _ConfigInvalid = 110
    _ScriptRunning = 111
    _scriptNotReady = 112

    def __init__(self, code=0, message="", uid=None, timestamp=None):
        self._error = ErrorMessage(
            code=code,
            message=message,
            data={},
            timestamp=timestamp if timestamp is not None else int(time.time()*1000),
            uuid=uid if uid is not None else str(uuid.uuid1())
        )

    @property
    def error(self):
        return self._error

    @error.setter
    def error(self, error):
        self._error = error

    @property
    def data(self):
        return self._error.data

    @data.setter
    def data(self, data):
        self._error.data = data

    @property
    def timestamp(self):
        return self._error.timestamp

    @timestamp.setter
    def timestamp(self, timestamp):
        self._error.timestamp = timestamp

    @property
    def uuid(self):
        return self._error.uuid

    @uuid.setter
    def uuid(self, uuid):
        self._error.uuid = uuid


class InvalidRequest(RequestException):
    """
    raise this exception when request is invalid
    """
    def __init__(self, message, uuid=None, timestamp=None):
        super().__init__(self._InvalidPayload, f'{self.__class__.__name__}: {message}', uuid, timestamp)


class DeviceNotFound(RequestException):
    """
    raise this exception when request target is not found
    """
    def __init__(self, mac, uuid=None, timestamp=None):
        super().__init__(self._DeviceNotFound, f'{self.__class__.__name__}: {mac}', uuid, timestamp)


class DeviceOffline(RequestException):
    """
    raise this exception when request target is not connect
    """
    def __init__(self, mac, uuid=None, timestamp=None):
        super().__init__(self._DeviceOffline, f'{self.__class__.__name__}: {mac}', uuid, timestamp)


class DeviceNotReady(RequestException):
    """
        raise this exception when device state is not ready for operation
    """

    def __init__(self, mac, uuid=None, timestamp=None):
        super().__init__(self._DeviceNotReady, f'{self.__class__.__name__}: {mac}', uuid, timestamp)


class Unreachable(RequestException):
    """
        raise this exception when device is on a unreachable simulator
    """

    def __init__(self, mac, uuid=None, timestamp=None):
        super().__init__(self._Unreachable, f'{self.__class__.__name__}: {mac}', uuid, timestamp)


class InvalidPayload(RequestException):
    """
    raise this exception when request payload is invalid
    """
    def __init__(self, message, uuid=None, timestamp=None):
        super().__init__(self._InvalidPayload, f'{self.__class__.__name__}:{message}', uuid, timestamp)


class Unsupported(RequestException):
    """
    raise this exception when command is not support
    """
    def __init__(self, message, uuid=None, timestamp=None):
        super().__init__(self._Unsupported, f'{self.__class__.__name__}: {message}', uuid, timestamp)


class NotFound(RequestException):
    """
    raise this exception when items not found, e.g. filename
    """
    def __init__(self, message, uuid=None, timestamp=None):
        super().__init__(self._NotFound, f'{self.__class__.__name__}: {message}', uuid, timestamp)


class OutOfRange(RequestException):
    """
    raise this exception when target value is out of range
    """
    def __init__(self, value, range, uuid=None, timestamp=None):
        super().__init__(self._OutOfRange, f'{self.__class__.__name__}: {value} not in {range}', uuid, timestamp)


class Timeout(RequestException):
    """
    raise this exception when target value is out of range
    """
    def __init__(self, uuid=None, timestamp=None):
        super().__init__(self._Timeout, f'{self.__class__.__name__}', uuid, timestamp)


class ConfigInvalid(RequestException):
    """
    raise this exception when the config of script is invalid
    """
    def __init__(self, uuid=None, timestamp=None):
        super().__init__(self._ConfigInvalid, f'{self.__class__.__name__}', uuid, timestamp)


class ScriptRunning(RequestException):
    """
    raise this exception when a same script is running
    """
    def __init__(self, uuid=None, timestamp=None):
        super().__init__(self._ScriptRunning, f'{self.__class__.__name__}', uuid, timestamp)


class ScriptNotReady(RequestException):
    """
    raise this exception when a same script is running
    """
    def __init__(self, uuid=None, timestamp=None):
        super().__init__(self._ScriptNotReady, f'{self.__class__.__name__}', uuid, timestamp)

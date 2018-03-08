import abc
import time
import json
from . import proto_codes
from . import example
from . import log


class IMessage(abc.ABC):
    @abc.abstractmethod
    def serialize(self) -> bytes:
        pass

    @abc.abstractclassmethod
    def deserialize(self, msg: bytes) -> 'IMessage':
        pass


class AbstractMessage(IMessage):
    def serialize(self) -> bytes:
        return str(self).encode('utf-8')


class Responce(AbstractMessage):
    def __init__(self, code: int, msg: str, time: int):
        assert code in proto_codes.ProtoCodes, 'Unknown code {}'.format(code)
        log.LOGGER.debug('Made {} of {}'.format(self.__class__.__name__, code))
        self.code = code
        self.msg = msg
        self.time = time

    def __str__(self):
        return json.dumps({
            'code': self.code,
            'msg': self.msg,
            'time': self.time
        })

    @classmethod
    def deserialize(cls, msg: bytes) -> 'Responce':
        return cls(**json.loads(msg.decode('utf-8')))


class Request(AbstractMessage):
    def __init__(self, act: str, src: str, dst: str, data: str, time: int):
        assert act in proto_codes.ProtoActions, 'Unknown action {}'.format(act)
        log.LOGGER.debug('Made {} of {}'.format(self.__class__.__name__, act))
        self.act = act
        self.src = src
        self.dst = dst
        self.data = data
        self.time = time

    def __str__(self):
        return json.dumps({
            'act': self.act,
            'src': self.src,
            'dst': self.dst,
            'data': self.data,
            'time': self.time
        })

    @classmethod
    def deserialize(cls, msg: bytes) -> 'Request':
        return cls(**json.loads(msg.decode('utf-8')))


@example.singleton
class MessageFab(object):
    GROUP_IDENTIFER = '#'
    USER_DENTIFER = '@'

    @staticmethod
    def deserialize(message: bytes) -> IMessage:
        exs = []
        try:
            return Responce.deserialize(message)
        except Exception as ex:
            exs.append(ex)
        try:
            return Request.deserialize(message)
        except Exception as ex:
            exs.append(ex)
        log.LOGGER.critical('Can\'t handle {} and {}'.format(*exs))
        raise TypeError('Can\'t deserialize {}'.format(message))

    def __init__(self, src=None):
        self.src = src

    @property
    def _get_time(self):
        return time.time()

    def make_req_presence(self, dst=None, data=None):
        return Request(
            proto_codes.ProtoActions.presence,
            self.src, dst, data, self._get_time)

    def make_req_prоbe(self, dst=None, data=None):
        return Request(
            proto_codes.ProtoActions.probe,
            self.src, dst, data, self._get_time)

    def make_req_msg(self, dst, data):
        return Request(
            proto_codes.ProtoActions.msg,
            self.src, dst, data, self._get_time)

    def make_req_quit(self, data, dst=None):
        return Request(
            proto_codes.ProtoActions.quit,
            self.src, dst, data, self._get_time)

    def make_req_authenticate(self, dst=None, data=None):
        return Request(
            proto_codes.ProtoActions.authenticate,
            self.src, dst, data, self._get_time)

    def make_req_join(self, dst, data):
        return Request(
            proto_codes.ProtoActions.join,
            self.src, dst, data, self._get_time)

    def make_req_leave(self, dst, data):
        return Request(
            proto_codes.ProtoActions.leave,
            self.src, dst, data, self._get_time)

    def make_resp_info(self, msg='Base info'):
        return Responce(
            proto_codes.ProtoCodes.base_info,
            msg, self._get_time)

    def make_resp_ok(self):
        return Responce(
            proto_codes.ProtoCodes.ok,
            'OK', self._get_time)

    def make_resp_forbidden(self):
        return Responce(
            proto_codes.ProtoCodes.forbidden,
            'Forbidden', self._get_time)

    def make_resp_error(self):
        return Responce(
            proto_codes.ProtoCodes.internal_error,
            'Sorry, we\'re working on it :(',
            self._get_time)


if __name__ == '__main__':
    log.setup_logger('debug')
    fab = MessageFab('client-name')
    msg = fab.make_req_msg('dst', 'data')
    print('msg1', msg)
    print('msg2', msg.serialize())

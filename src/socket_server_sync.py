import time
from . import socket_server
from . import log


class SocketServerSync(object):
    @staticmethod
    def deserialize_msg(msg: bytes) -> str:
        return msg.encode('utf-8')

    def __init__(self, address, port):
        self.is_running = False
        self.address = address
        self.port = port

    @log.log(__qualname__)
    def listen_and_answer(self, socket_, message):
        client, address = socket_.accept()
        client.send(self.deserialize_msg(message))
        client.close()
        return 'Connected client from {}'.format(address)

    def stop(self, socket_):
        self.is_running = False
        socket_.close()
        log.LOGGER.debug('Connection closed')

    def execute(self):
        self.is_running = True
        socket_ = socket_server.make_tcp_socket(self.address, self.port, 1)
        while self.is_running:
            try:
                self.listen_and_answer(socket_, time.ctime(time.time()) + '\n')
            except KeyboardInterrupt:
                self.stop(socket_)


def process(address='', port=8888):
    srv = SocketServerSync(address, port)
    srv.execute()

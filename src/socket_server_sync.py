import time
from . import socket_server


class SocketServerSync(object):
    @staticmethod
    def deserialize_msg(msg: bytes) -> str:
        return msg.encode('utf-8')

    def __init__(self, address, port):
        self.is_running = False
        self.address = address
        self.port = port

    def listen_and_answer(self, socket, message):
        client, address = socket.accept()
        client.send(self.deserialize_msg(message))
        client.close()
        return 'Connected client from {}'.format(address)

    def stop(self):
        self.is_running = False
        self.socket.close()
        print('Correctly closing')

    def execute(self):
        self.is_running = True
        socket_ = socket_server.make_tcp_socket(self.address, self.port, 1)
        while self.is_running:
            print(
                self.listen_and_answer(socket_, time.ctime(time.time()) + '\n')
            )


def process(address='', port=8888):
    srv = SocketServerSync(address, port)
    try:
        srv.execute()
    except KeyboardInterrupt:
        srv.stop()

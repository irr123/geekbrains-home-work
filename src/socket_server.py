import socket
import time

_is_sending_time = None


def make_tcp_socket(address: str, port: int) -> socket.socket:
    socket_ = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_.bind((address, port))
    socket_.listen(5)
    return socket_


def send_time(socket_: socket.socket) -> None:
    while _is_sending_time:
        client, address = socket_.accept()
        print('Connected client from {}'.format(address))
        payload = time.ctime(time.time()) + '\n'
        client.send(payload.encode('ascii'))
        client.close()


def process(address='', port=8888):
    global _is_sending_time
    _is_sending_time = True
    socket_ = make_tcp_socket(address, port)
    try:
        send_time(socket_)
    except KeyboardInterrupt:
        _is_sending_time = False
        socket_.close()
        print('Correctly closing')

import select
import socket
import time

_is_sending_time = None


def make_tcp_socket(address: str, port: int, blocking: int) -> socket.socket:
    socket_ = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_.setblocking(blocking)
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


def send_time_non_blocking(socket_: socket.socket) -> None:
    while _is_sending_time:
        is_ready = select.select((socket_,), tuple(), tuple(), 1)
        if not is_ready[0]:
            print('Not ready')
            continue

        client, address = socket_.accept()
        print('Connected client from {}'.format(address))
        payload = time.ctime(time.time()) + '\n'
        client.send(payload.encode('ascii'))
        client.close()


def process(address='', port=8888, blocking=1):
    global _is_sending_time
    _is_sending_time = True
    socket_ = make_tcp_socket(address, port, blocking)
    method = send_time if blocking == 1 else send_time_non_blocking
    try:
        method(socket_)
    except KeyboardInterrupt:
        _is_sending_time = False
        socket_.close()
        print('Correctly closing')

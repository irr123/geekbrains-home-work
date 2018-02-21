import socket


def make_tcp_socket(address: str = 'localhost',
                    port: int = 8888) -> socket.socket:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((address, port))
    return s


def recive_time(socket_: socket.socket) -> None:
    payload = socket_.recv(1024)
    socket_.close()
    print('Received time is {}'.format(payload.decode('ascii')))


def process(address='', port=8888):
    socket_ = make_tcp_socket(address, port)
    recive_time(socket_)

import socket
import threading
import queue
import random
from . import connection
from . import log
from . import proto


def make_tcp_socket(address: str = 'localhost',
                    port: int = 8888, blocking=False) -> socket.socket:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setblocking(1 if blocking else 0)
    ret = -1
    if blocking:
        s.connect((address, port))
    else:
        ret = s.connect_ex((address, port))
    log.LOGGER.debug(
        'Connecting to {}:{} => {}'.format(address, port, ret))
    return s


def recive_time(socket_: socket.socket) -> None:
    socket_.send(b'waaaazzzzaaauuupppp???')
    payload = socket_.recv(1024)
    socket_.close()
    print('[Received]: {}'.format(payload.decode('ascii')))


def fn_process(address='', port=8888, blocking=False):
    socket_ = make_tcp_socket(address, port, blocking)
    recive_time(socket_)


class BackgroundClient(object):
    def __init__(
            self, address, port, conn_factory, protocol, in_queue, out_queue):
        self.is_running = False
        self.addr_port = (address, port)
        self.conn_fab = conn_factory
        self.in_queue = in_queue
        self.out_queue = out_queue
        self.proto = protocol

    def listen_and_messaging(
            self, conn: connection.IConnection, use_blocking=False):
        if conn.is_ready_to_read():
            message = conn.read()
            if message:
                # self.in_queue.put(self.deserialize_msg(message))
                print('[Received]: {}'.format(
                    self.proto.deserialize(message)))

        if conn.is_ready_to_write():
            if not self.out_queue.empty():
                msg = self.out_queue.get()
                conn.write(self.proto.make_req_msg('default', msg).serialize())

    def stop(self):
        self.is_running = False
        self.conn_fab.close_all_connections()
        log.LOGGER.debug('{} stopped.'.format(self.__class__.__name__))

    def execute(self, use_blocking=False):
        self.is_running = True
        sock = make_tcp_socket(*self.addr_port, use_blocking)
        conn = self.conn_fab.add_connection(self.addr_port, sock, use_blocking)
        while self.is_running:
            try:
                self.listen_and_messaging(conn, use_blocking)
            except KeyboardInterrupt:
                self.stop()


class Client(object):
    def __init__(
            self, address, port, conn_factory, protocol,
            in_queue, out_queue, use_blocking=False):
        self.in_queue = in_queue
        self.out_queue = out_queue
        self.client = BackgroundClient(
            address, port, conn_factory, protocol, in_queue, out_queue)
        self.thread = threading.Thread(
            target=self.client.execute,
            kwargs={'use_blocking': use_blocking})

    def working_method(self, *args, **kwargs):
        message = input('Write your message here: ')
        if message:
            self.out_queue.put(message)

    def execute(self):
        self.thread.start()
        while self.client.is_running:
            try:
                self.working_method()
            except KeyboardInterrupt:
                self.stop()

    def stop(self):
        log.LOGGER.debug('Stop {}'.format(self.thread))
        self.client.stop()
        self.thread.join()


def process(address, port, blocking=False):
    fab = connection.ConnectionFab()
    protocol = proto.MessageFab('client-{}'.format(random.randint(0, 99)))
    in_queue = queue.Queue()
    out_queue = queue.Queue()
    client = Client(
        address, port, fab, protocol, in_queue, out_queue, blocking)
    client.execute()

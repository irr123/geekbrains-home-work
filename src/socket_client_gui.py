import threading
import queue
import random
from . import connection
from . import log
from . import proto
from . import proto_codes
from . import models
from . import socket_client
from . import simple_ui


class BackgroundClient(object):
    def __init__(
            self, address, port, conn_factory, protocol, in_queue, out_queue):
        self.is_running = False
        self.addr_port = (address, port)
        self.conn_fab = conn_factory
        self.in_queue = in_queue
        self.out_queue = out_queue
        self.proto = protocol
        self.gui = None
        self.key = None
        self.not_authen = True

    def listen_and_messaging(
            self, conn: connection.IConnection, use_blocking=False):
        if conn.is_ready_to_read():
            msg = conn.read()
            if msg:
                de_msg = self.proto.deserialize(msg)
                if isinstance(de_msg, proto.Responce):
                    if de_msg.code == proto_codes.ProtoCodes.important_info:
                        log.LOGGER.info('Set key {}'.format(de_msg.msg))
                        self.key = de_msg.msg
                else:
                    self.gui.r_handler(
                        '[{}] {}'.format(de_msg.time, de_msg.src),
                        self.proto.decrypt(de_msg.data, self.key))

        if conn.is_ready_to_write():
            if self.not_authen and (not self.key):
                conn.write(self.proto.make_req_authenticate().serialize())
                self.not_authen = False
            elif not self.out_queue.empty():
                msg = self.out_queue.get()
                if not msg:
                    return
                msg_object = self.proto.make_req_msg('default', msg)
                msg_object.data = self.proto.encrypt(msg_object.data, self.key)
                conn.write(msg_object.serialize())

    def stop(self):
        self.is_running = False
        self.conn_fab.close_all_connections()
        log.LOGGER.debug('{} stopped.'.format(self.__class__.__name__))

    def execute(self, use_blocking=False):
        self.is_running = True
        sock = socket_client.make_tcp_socket(*self.addr_port, use_blocking)
        conn = self.conn_fab.add_connection(self.addr_port, sock, use_blocking)
        for msg in models.get_msgs_by_client_addr(conn.addr_port):
            # self.in_queue.put((
            #     '{}:{}'.format(*conn.addr_port),
            #     self.proto.deserialize(msg)))
            self.gui.r_handler('{}:{}'.format(*self.addr_port),
                               self.proto.deserialize(msg))
        while self.is_running:
            try:
                self.listen_and_messaging(conn, use_blocking)
            except KeyboardInterrupt:
                self.stop()


class Client(object):
    def __init__(
            self, address, port, conn_factory, protocol,
            in_queue, out_queue, gui_factory, use_blocking=False):
        self.in_queue = in_queue
        self.out_queue = out_queue
        self.client = BackgroundClient(
            address, port, conn_factory, protocol, in_queue, out_queue)
        self.thread = threading.Thread(
            target=self.client.execute,
            kwargs={'use_blocking': use_blocking})
        self.gui_factory = gui_factory
        self.gui = None

    def execute(self):
        self.thread.start()
        self.gui = self.gui_factory(self.send, self.receive, self.stop)
        self.client.gui = self.gui
        self.gui.start()

    def send(self, msg):
        self.out_queue.put(msg)

    def receive(self):
        return self.in_queue.get()

    def stop(self):
        print('STOP IT')
        log.LOGGER.debug('Stop {}'.format(self.thread))
        self.client.stop()
        self.thread.join()


def process(address, port, blocking=False):
    fab = connection.ConnectionFab()
    protocol = proto.MessageFab('client-{}'.format(random.randint(0, 99)))
    in_queue = queue.Queue()
    out_queue = queue.Queue()
    gui_fab = simple_ui.Gui  # lazy init
    client = Client(
        address, port, fab, protocol,
        in_queue, out_queue, gui_fab, blocking)
    client.execute()

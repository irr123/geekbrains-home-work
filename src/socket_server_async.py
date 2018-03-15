import random
from . import log
from . import connection
from . import proto
from . import proto_codes
from . import models


class SocketServerAsync(object):
    @staticmethod
    def deserialize_msg(msg: bytes) -> str:
        return msg.encode('utf-8')

    def __init__(self, address, port, conn_factory, protocol):
        self.is_running = False
        self.addr_port = (address, port)
        self.conn_fab = conn_factory
        self.proto = protocol
        self.msg_queue = {}

    def add_to_queue(self, identity, data):
        if identity not in self.msg_queue:
            self.msg_queue[identity] = []
        self.msg_queue[identity].append(data)

    def get_from_queue(self, identity):
        if identity in self.msg_queue:
            if len(self.msg_queue[identity]) > 0:
                return self.msg_queue[identity].pop()
        return None

    def listen_and_answer(self, conn: connection.IConnection, use_blocking):
        if conn.is_ready_to_read():
            client_conn = conn.accept(use_blocking)
            self.add_to_queue(client_conn.addr_port, self.proto.make_resp_info('Success'))
            models.add_client(client_conn.addr_port)

        for client_conn in self.conn_fab.get_all_clients(
                exclude_addr_port=[self.addr_port]):

            if not client_conn.is_valid:
                self.conn_fab.remove_invalid_client(client_conn.addr_port)
                continue

            if client_conn.is_ready_to_read():
                raw_message = client_conn.read()
                if not raw_message:
                    continue

                message = self.proto.deserialize(raw_message)
                client = models.get_client_by_addr(client_conn.addr_port)
                if isinstance(message, proto.Request):
                    message.data = self.proto.decrypt(message.data, client.clientkey)
                    models.add_message(client, message.data)

                answer_msg = None
                if client_conn.is_ready_to_write():
                    if message.act == proto_codes.ProtoActions.authenticate:
                        key = random.randint(1, 1000)
                        models.add_client_key(client, key)
                        log.LOGGER.info('Make key {} for {}:{}'.format(key, *client_conn.addr_port))
                        answer_msg = self.proto.make_resp_auth_ok(key)
                    else:
                        answer_msg = self.proto.make_resp_ok()
                    client_conn.write(answer_msg.serialize())
                else:
                    self.add_to_queue(client_conn.addr_port, answer_msg)

                for other_client_conn in self.conn_fab.get_all_clients(
                        [self.addr_port, client_conn.addr_port]):
                    self.add_to_queue(other_client_conn.addr_port, message)

            if client_conn.is_ready_to_write():
                delayed_msg = self.get_from_queue(client_conn.addr_port)
                if delayed_msg:
                    if isinstance(delayed_msg, proto.Request):
                        client = models.get_client_by_addr(client_conn.addr_port)
                        encrypted = self.proto.encrypt(delayed_msg.data, client.clientkey)
                        delayed_msg.data = encrypted
                    client_conn.write(delayed_msg.serialize())

    def stop(self):
        self.is_running = False
        self.conn_fab.close_all_connections()
        log.LOGGER.debug('{} stopped.'.format(self.__class__.__name__))

    def execute(self, use_blocking=False):
        self.is_running = True
        conn = self.conn_fab.get_connection(*self.addr_port, use_blocking)
        while self.is_running:
            try:
                self.listen_and_answer(conn, use_blocking)
            except KeyboardInterrupt:
                self.stop()


def process(address='127.0.0.1', port=8888, blocking=False):
    srv = SocketServerAsync(
        address, port, connection.ConnectionFab(),
        proto.MessageFab('Main-srv'))
    srv.execute(blocking)

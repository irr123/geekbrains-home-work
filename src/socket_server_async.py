from . import log
from . import connection


class SocketServerAsync(object):
    @staticmethod
    def deserialize_msg(msg: bytes) -> str:
        return msg.encode('utf-8')

    def __init__(self, address, port, conn_factory):
        self.is_running = False
        self.addr_port = (address, port)
        self.conn_fab = conn_factory

    def listen_and_answer(self, conn: connection.IConnection, use_blocking):
        if conn.is_ready_to_read():
            client_conn = conn.accept(use_blocking)

        for client_conn in self.conn_fab.get_all_clients(
                exclude_addr_port=[self.addr_port]):

            if not client_conn.is_valid:
                self.conn_fab.remove_invalid_client(client_conn.addr_port)
                continue

            if client_conn.is_ready_to_read():
                message = client_conn.read()
                if not message:
                    continue

                for other_client_conn in self.conn_fab.get_all_clients(
                        [self.addr_port, client_conn.addr_port]):
                    if other_client_conn.is_ready_to_write():
                        other_client_conn.write(message)

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
        address, port, connection.ConnectionFab())
    srv.execute(blocking)

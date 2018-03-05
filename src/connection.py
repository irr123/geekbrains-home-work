import socket
import select
from . import example
from . import log
from . import socket_server


class IConnection(object):
    @property
    def addr_port(self) -> tuple:
        raise NotImplementedError('Sub-class must implement this method')

    @property
    def is_valid(self) -> True:
        raise NotImplementedError('Sub-class must implement this method')

    def is_ready_to_read(self) -> bool:
        raise NotImplementedError('Sub-class must implement this method')

    def is_ready_to_write(self) -> bool:
        raise NotImplementedError('Sub-class must implement this method')

    def read(self) -> bytes:
        raise NotImplementedError('Sub-class must implement this method')

    def write(self, data: bytes) -> int:
        raise NotImplementedError('Sub-class must implement this method')

    def accept(self) -> 'IConnection':
        raise NotImplementedError('Sub-class must implement this method')

    def close(self) -> None:
        raise NotImplementedError('Sub-class must implement this method')


class BlockingConnection(IConnection):
    default_chunk_size = 1024

    def __init__(self, addr_port: tuple, socket_: socket.socket):
        self._addr_port = addr_port
        self._is_valid = True
        self._socket = socket_
        self._fail_count = 0

    def __str__(self) -> str:
        mark = ''
        if not self.is_valid:
            mark = 'Invalid '
        return '{}{}:{} {}'.format(
            mark, *self.addr_port, self._socket)

    @property
    def addr_port(self) -> tuple:
        return self._addr_port

    @property
    def is_valid(self) -> bool:
        return self._is_valid

    def is_ready_to_read(self) -> bool:
        return self.is_valid

    def is_ready_to_write(self) -> bool:
        return self.is_valid

    def accept(self, use_blocking=False) -> IConnection:
        client_socket, client_address = self._socket.accept()
        fab = ConnectionFab()
        return fab.add_connection(client_address, client_socket, use_blocking)

    def read(self) -> bytes:
        ret = b''
        try:
            ret = self._socket.recv(self.default_chunk_size)
        except Exception as ex:
            self._is_valid = False
            log.LOGGER.debug(
                'Exception <{}> happens while read from {}:{}'
                .format(ex, *self.addr_port))
        if not ret:
            self._fail_count += 1
            if self._fail_count > 3:
                self._is_valid = False
                log.LOGGER.info(
                    'Mark {}:{} as FAILED'.format(*self.addr_port))
        else:
            self._fail_count = 0
        log.LOGGER.debug('Read {} from {}:{}'.format(ret, *self.addr_port))
        return ret

    def write(self, data: bytes) -> int:
        log.LOGGER.debug('Writting {} to {}:{}'.format(data, *self.addr_port))
        try:
            return self._socket.send(data)
        except Exception as ex:
            self._is_valid = False
            log.LOGGER.debug(
                'Exception <{}> happens while write to {}:{}'
                .format(ex, *self.addr_port))
        return 0

    def close(self) -> None:
        log.LOGGER.debug(
            'Closing {} with {}:{}'
            .format(self.__class__.__name__, *self.addr_port))
        try:
            self._socket.shutdown(socket.SHUT_RDWR)
            return self._socket.close()
        except Exception as ex:
            self._is_valid = False
            log.LOGGER.debug(
                'Exception <{}> happens while closing {}:{}'
                .format(ex, *self.addr_port))
        return None


class Connection(BlockingConnection):
    wait_timeout = 1

    def is_ready_to_read(self) -> bool:
        if not self.is_valid:
            return False
        try:
            r, w, e = select.select(
                (self._socket,), tuple(), tuple(), self.wait_timeout)
        except Exception as ex:
            r = False
            log.LOGGER.warn(
                'Exception <{}> happens while check is ready to read {}:{}'
                .format(ex, *self.addr_port))
        return bool(r)

    def is_ready_to_write(self) -> bool:
        if not self.is_valid:
            return False
        try:
            r, w, e = select.select(
                tuple(), (self._socket,), tuple(), self.wait_timeout)
        except Exception as ex:
            w = False
            log.LOGGER.warn(
                'Exception <{}> happens while check is ready to write {}:{}'
                .format(ex, *self.addr_port))
        return bool(w)


@example.singleton
class ConnectionFab(object):
    def __init__(self):
        self.connections = {}

    @staticmethod
    def _make_connection(
            addr_port: tuple, use_blocking: bool) -> IConnection:
        conn_cls = BlockingConnection if use_blocking else Connection
        log.LOGGER.debug(
            'Making new {} with {}:{} ({})'
            .format(conn_cls.__name__, *addr_port, use_blocking))
        socket_ = socket_server.make_tcp_socket(
            *addr_port, 1 if use_blocking else 0)
        return conn_cls(addr_port, socket_)

    def add_connection(
            self, addr_port, socket_, use_blocking=False) -> IConnection:
        conn_cls = BlockingConnection if use_blocking else Connection
        log.LOGGER.debug(
            'Adding new {} with {}:{} ({})'
            .format(conn_cls.__name__, *addr_port, use_blocking))
        conn = conn_cls(addr_port, socket_)
        self.connections[addr_port] = conn
        return conn

    def get_connection(
            self, address: str, port: int, use_blocking=False) -> IConnection:
        addr_port = (address, port)
        curr_connection = self.connections.get(addr_port)
        if curr_connection:
            return curr_connection

        curr_connection = self._make_connection(addr_port, use_blocking)
        self.connections[addr_port] = curr_connection
        return curr_connection

    def get_all_clients(self, exclude_addr_port: list = None) -> list:
        """ Acceptable format of exclude_addr_port is
        [(addr1, port1), (addr2, port2), ...]
        """
        if not exclude_addr_port:
            return self.connections.copy().values()

        filtered = filter(lambda item: item[0] not in exclude_addr_port,
                          self.connections.copy().items())
        return map(lambda item: item[1], filtered)

    def remove_invalid_client(self, addr_port: tuple) -> None:
        if addr_port in self.connections:
            self.connections[addr_port].close()
            log.LOGGER.debug('Removing {}'.format(self.connections[addr_port]))
            del self.connections[addr_port]

    def close_all_connections(self) -> None:
        for addr_port, conn in self.connections.items():
            conn.close()

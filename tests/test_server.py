import pytest
import pytest_socket
import src


class SocketMock(object):
    def accept(self):
        print('Accept')
        return SocketMock(), '127.0.0.1'

    def send(self, msg):
        print('Send')

    def close(self):
        print('Close')


def make_mock_socket():
    return SocketMock()


@pytest.fixture
def socket_fixture():
    return make_mock_socket()


def test_encode():
    b'byte-string' == 'byte-string'.encode('ascii')


def test_if_it_mocked():
    srv = src.socket_server_sync.SocketServerSync('', 8888)
    with pytest.raises(pytest_socket.SocketBlockedError):
        srv.execute()


def test_listen_and_answer():
    srv = src.socket_server_sync.SocketServerSync('', 8888)
    ret = srv.listen_and_answer(
        make_mock_socket(),
        'any_message'
    )
    assert ret == 'Connected client from 127.0.0.1'


def test_listen_and_answer_parametirzed(socket_fixture):
    client_socket, client_address = socket_fixture.accept()
    socket_fixture.close()
    assert client_address == '127.0.0.1'

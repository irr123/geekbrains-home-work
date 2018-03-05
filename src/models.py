import os
from sqlalchemy import create_engine
from sqlalchemy import Table, Column, \
    Integer, Numeric, String, MetaData, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from . import log


DB_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'server.db')
log.LOGGER.debug('DB path: {}'.format(DB_PATH))
engine = create_engine('sqlite:///{}'.format(DB_PATH), echo=True)
session_maker = sessionmaker(bind=engine)
session = session_maker()
Base = declarative_base()


class Client(Base):
    __tablename__ = 'Client'

    clientid = Column(Integer, primary_key=True)
    clientaddress = Column(String)

    def __init__(self, clientaddress):
        self.clientaddress = clientaddress

    def __str__(self):
        return '{}'.format(self.clientaddress)


class Message(Base):
    __tablename__ = 'Message'

    messageid = Column(Integer, primary_key=True)
    clientid = Column(Integer, ForeignKey('Client.clientid'))
    messagebody = Column(String)

    def __init__(self, clientid, messagebody):
        self.clientid = clientid
        self.messagebody = messagebody

    def __str__(self):
        return '<{}> {}'.format(self.clientid, self.messagebody)


if not os.path.exists(DB_PATH):
    log.LOGGER.debug('Not exist, creating: {}'.format(DB_PATH))
    Base.metadata.create_all(engine)


def add_client(address):
    c = Client('{}:{}'.format(*address))
    session.add(c)
    session.commit()


def add_message(client, message):
    m = Message(client.clientid, message)
    session.add(m)
    session.commit()


def get_client_by_addr(address):
    return session\
        .query(Client)\
        .filter(Client.clientaddress == '{}:{}'.format(*address))\
        .one_or_none()


def get_msgs_by_client_addr(address):
    c = get_client_by_addr(address)
    if not c:
        return []

    return session\
        .query(Message)\
        .filter(Message.clientid == c.clientid)


if __name__ == '__main__':
    log.setup_logger('debug')
    clients = [
        Client('10.10.10.1'),
        Client('10.10.10.2'),
        Client('10.10.10.3')
    ]
    session.add_all(clients)
    session.commit()

    msgs = [
        Message(clients[0].clientid, 'msg1'),
        Message(clients[0].clientid, 'msg2'),
        Message(clients[0].clientid, 'msg3')
    ]

    session.add_all(msgs)
    session.commit()

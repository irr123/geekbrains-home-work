import os

from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, Numeric, String, MetaData, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from sqlalchemy.orm import relationship


# Понял, что эту таблицу можно создать как в примере после создания базы, но вот вопрос: какой из способов более правильный?

# class ContactList(Base):
#     __tablename__ = 'contact_list'
#     id_parent = Column(Integer, nullable=True)
#     id_client = Column(Integer, nullable=True)
#
#     def __init__(self, id_parent, id_client):
#         self._id_parent = id_parent
#         self._id_client = id_client


# if __name__ == '__main__':
#     if 'server.db' not in os.listdir():

Server_DB = create_engine('sqlite:///server.db', echo=True)
Session_Server = sessionmaker(bind=Server_DB)
Base = declarative_base()

association_table = Table('ContactList', Base.metadata,
                          Column('id_parent', Integer, ForeignKey('Client.id')),
                          Column('id_client', Integer, ForeignKey('Client.id'))
                          )


class Client(Base):
    __tablename__ = 'Client'
    id = Column(Integer, nullable=False, primary_key=True, autoincrement=True, unique=True)
    login = Column(String, nullable=False, unique=True)
    information = Column(String, nullable=True)

    def __init__(self, id, login, information):
        self.id = id
        self.login = login
        self.information = information

    def __repr__(self):
        return 'Client name: {}, info: {}'.format(self._login, self._information)


class ClientHistory(Base):
    __tablename__ = 'ClientHistory'
    id_client = Column(Integer, ForeignKey('Client.id'), nullable=False, primary_key=True)
    time_in = Column(Integer, nullable=False)
    ip_address = Column(Integer, nullable=False)

    def __init__(self, id_client, time_in, ip_address):
        self.id_client = id_client
        self.time_in = time_in
        self.ip_address = ip_address

    def __repr__(self):
        return ''


Client.children = relationship('ClientHistory', back_populates='parent')
Base.metadata.create_all(Server_DB)


Client_DB = create_engine('sqlite:///client.db', echo=True)
Session_Client = sessionmaker(bind=Client_DB)
Base = declarative_base()


class ContactList(Base):
    __tablename__ = 'ContactList'
    id = Column(Integer, nullable=False, primary_key=True, autoincrement=True, unique=True)
    name = Column(String, nullable=False)
    info = Column(String)

    def __init__(self, id, name, info):
        self._id = id
        self._name = name
        self._info = info

    def __repr__(self):
        return 'Friend name: {}, info: {}'.format(self._name, self._info)


class History(Base):
    __tablename__ = 'History'
    id_friend = Column(Integer, ForeignKey('ContactList.id'), primary_key=True, nullable=False)
    massages = Column(String, nullable=False)
    date = Column(Integer, nullable=False)

    def __init__(self, id_friend, massage, date):
        self._id_friend = id_friend
        self._massage = massage
        self._date = date

    # def __repr__(self):

Base.metadata.create_all(Client_DB)

session = Session_Server()
client = Client('Robenzon', 'IslandMen', 'info')
session.add_all(client)
session.commit()

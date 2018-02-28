from collections import namedtuple

_ProtoCodes = namedtuple('ProtoCodes', [
    'base_info', 'important_info', 'ok',
    'created', 'accepted', 'invalid_request',
    'not_authorized', 'incorrect_login_pass',
    'forbidden', 'not_found', 'conflict',
    'gone', 'internal_error'])

ProtoCodes = _ProtoCodes(
    100, 101, 200, 201, 202, 400, 401, 402,
    403, 404, 409, 410, 500)

_ProtoActions = namedtuple('ProtoActions', [
    'presence', 'prоbe', 'msg', 'quit',
    'authenticate', 'join', 'leave'])

ProtoActions = _ProtoActions(
    'presence', 'prоbe', 'msg', 'quit',
    'authenticate', 'join', 'leave')

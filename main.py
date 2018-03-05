#!/usr/bin/env python

import argparse
import src


AVAILABLE_WORKERS = {
    'fn-client': lambda bl: lambda addr, port:
    src.socket_client.fn_process(addr, port, bl),

    'fn-server': lambda bl: lambda addr, port:
    src.socket_server.process(addr, port, blocking=bl),

    'cl-server': lambda bl: lambda addr, port:
    src.socket_server_sync.process(addr, port),

    'server': lambda bl: lambda addr, port:
    src.socket_server_async.process(addr, port, blocking=bl),

    'client': lambda bl: lambda addr, port:
    src.socket_client.process(addr, port, blocking=bl)
}


def parce_params():
    parser = argparse.ArgumentParser(description='Socket example')
    parser.add_argument(
        'mode', type=str,
        help='mode is one of [{}]'.format(
            ', '.join(AVAILABLE_WORKERS.keys())))

    parser.add_argument('-address', type=str, default='127.0.0.1')
    parser.add_argument('-port', type=int, default=8000)

    parser.add_argument(
        '--blocking', type=int, default=1,
        help='blocking or non-blocking sockets using in server, 1 or 0')

    parser.add_argument(
        '--log-level', type=str, default='debug',
        help='available params is {}'.format(
            ', '.join(src.log.LOG_LEVEL.keys())))
    return parser.parse_args()


def main():
    args = parce_params()
    src.log.setup_logger(args.log_level.lower())
    src.log.LOGGER.info(args)

    worker = AVAILABLE_WORKERS.get(
        args.mode,
        lambda x: lambda: print('`{}`-mode not found'.format(args.mode)))
    worker(args.blocking)(args.address, args.port)


if __name__ == '__main__':
    main()
    # new_fn = src.example.averager()
    # help(new_fn)
    # new_fn('param1', 100)
    # new_fn('param2', 100, min=100, max=200)
    # new_fn('param3', 100)

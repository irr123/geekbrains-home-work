#!/usr/bin/env python

import logging
import argparse
import src
# import example


AVAILABLE_WORKERS = {
    'client': lambda x: src.socket_client.process,
    'fn-server': lambda x: src.socket_server.process(blocking=x),
    'cl-server': lambda x: src.socket_server_sync.process
}


def parce_params():
    parser = argparse.ArgumentParser(description='Socket example')
    parser.add_argument(
        'mode', type=str,
        help='mode is one of [{}]'.format(
            ', '.join(AVAILABLE_WORKERS.keys())))

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
    worker(args.blocking)()


if __name__ == '__main__':
    main()
    # new_fn = example.averager()
    # help(new_fn)
    # new_fn('param1', 100)
    # new_fn('param2', 100, min=100, max=200)
    # new_fn('param3', 100)

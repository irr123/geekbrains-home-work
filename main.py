#!/usr/bin/env python

import argparse
import src

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
            ', '.join(x for x in AVAILABLE_WORKERS.keys())
        )
    )
    parser.add_argument(
        '--blocking', type=int, default=1,
        help='blocking or non-blocking sockets using in server, 1 or 0')
    return parser.parse_args()


def main():
    args = parce_params()
    print('Running with {}'.format(args))
    worker = AVAILABLE_WORKERS.get(
        args.mode,
        lambda: print('`{}`-mode not found'.format(args.mode))
    )
    worker(args.blocking)()


if __name__ == '__main__':
    main()

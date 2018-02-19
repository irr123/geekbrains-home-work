#!/usr/bin/env python

import argparse
import src


def parce_params():
    parser = argparse.ArgumentParser(description='Socket example')
    parser.add_argument('mode', type=str, help='mode is `client` or `server`')
    parser.add_argument(
        '--blocking', type=int, default=1,
        help='blocking or non-blocking sockets using in server, 1 or 0')
    return parser.parse_args()


def main():
    args = parce_params()
    print('Running with {}'.format(args))
    worker = {
        'client': src.socket_client.process,
        'server': lambda: src.socket_server.process(blocking=args.blocking)
    }.get(args.mode, lambda: print('`{}`-mode not found'.format(args.mode)))
    worker()


if __name__ == '__main__':
    main()

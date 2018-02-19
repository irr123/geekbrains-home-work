#!/usr/bin/env python

import argparse
import src


def parce_params():
    parser = argparse.ArgumentParser(description='Socket example')
    parser.add_argument('mode', type=str, help='mode is `client` or `server`')
    return parser.parse_args()


def main():
    mode = parce_params().mode
    worker = {
        'client': src.socket_client.process,
        'server': src.socket_server.process
    }.get(mode, lambda: print('`{}`-mode not found'.format(mode)))
    worker()


if __name__ == '__main__':
    main()

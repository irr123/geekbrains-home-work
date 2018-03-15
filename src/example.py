import random
import functools
import logging
import threading
import queue
import time
from . import log as logger


def log(name):
    def inner_log(fn):
        print('Decorator applyed')
        logger = logging.getLogger()

        @functools.wraps(fn)
        def wrap(*args, **kwargs):
            ret = fn(*args, **kwargs)
            logger.debug('[{}] {}'.format(name, ret))
            return ret
        return wrap
    return inner_log


def averager():
    series = []

    @log('example.py')
    def fn_my_cute_name(arg1, delta, min=0, max=99):
        """ my cute name
        """
        series.append(arg1)
        print(series)
        return random.randint(min, max) + delta
    return fn_my_cute_name


class ListTransaction(object):
    def __init__(self, data_list):
        self.list = data_list
        self.copy_ptr = None

    def __enter__(self):
        self.copy_ptr = self.list[:]
        return self.copy_ptr

    def __exit__(self, *args):
        if not args:
            self.list = self.copy_ptr
        return True


def singleton(fn):
    instances = {}

    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        nonlocal instances
        instance = instances.get(fn.__name__)
        if not instance:
            instance = fn(*args, **kwargs)
            logger.LOGGER.debug(
                'Make new instance of {} with {} and {}'
                .format(fn.__name__, args, kwargs))
            instances[fn.__name__] = instance
        return instance
    return wrapper


@singleton
class Server(object):
    def __init__(self):
        self.data = []

    def do(self):
        return '@'.join(self.data)

    def change_callback(self, data):
        print('change_callback')
        self.data.append(data)

    def clear_callback(self):
        print('clear_callback')
        self.data = []


STOP_FLAG = False


def put_data_into_queue(queue_: queue.Queue):
    s = Server()
    for i in range(100):
        print('Put {} into queue, with {}'.format(i, s.do()))
        queue_.put(i)
        if STOP_FLAG:
            break
        time.sleep(1)


if __name__ == '__main__':
    s1 = Server()
    # s2 = Server()

    q = queue.Queue()
    thread = threading.Thread(target=put_data_into_queue, args=(q,))
    thread.start()
    try:
        while True:
            i = q.get()
            print('Get {} from queue'.format(i))
            if i % 8:
                s1.change_callback('string-'.format(i))
            if i % 2:
                s1.clear_callback()
    except KeyboardInterrupt:
        STOP_FLAG = True
        thread.join()

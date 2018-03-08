import random
import functools
import logging
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
    pass


if __name__ == '__main__':
    # s1 = Server()
    # s2 = Server()

    d = {
        'a': 1,
        'b': 2,
        'c': 3
    }
    for key, value in d.items():
        print(key, value)

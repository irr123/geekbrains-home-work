import random
import functools
import logging


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
    instance = None
    def wrapper(*args, **kwargs):
        if not instance:
            instance = fn()
        return instance
    return wrapper


@singleton
class Server(object):
    pass


if __name__ == '__main__':
    s1 = Server()
    s2 = Server()

import sys
import functools
import logging


APP_NAME = 'Chat app'
LOGGER = logging.getLogger(APP_NAME)
LOG_LEVEL = {
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'warn': logging.WARN,
    'error': logging.ERROR,
    'critical': logging.CRITICAL,
}


def setup_logger(verbosity='debug'):
    handler = logging.StreamHandler(stream=sys.stdout)
    formatter = logging.Formatter(
        r'%(asctime)s [%(name)s] %(message)s', "%Y-%m-%d %H:%M:%S")
    handler.setFormatter(formatter)

    LOGGER.handlers = [handler]
    LOGGER.setLevel(LOG_LEVEL.get(verbosity))


def log(source=None):
    def inner_log(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            fn_ret = func(*args, **kwargs)
            if source:
                LOGGER.debug(
                    '[{}]: {}({} {}) => {}'
                    .format(source, func.__name__, args, kwargs, fn_ret))
            else:
                LOGGER.debug(
                    '{}({} {}) => {}'
                    .format(func.__name__, args, kwargs, fn_ret))
            return fn_ret
        return wrapper
    return inner_log

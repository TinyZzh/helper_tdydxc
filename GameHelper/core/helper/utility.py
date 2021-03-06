#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os
import json
import time
import inspect
import functools
import traceback


def init_logging():
    log_file_name = 'info.log'
    log_file_path = './logs/'
    if not os.path.exists(log_file_path):
        os.mkdir(log_file_path)
        pass
    log_path = os.path.join(log_file_path, log_file_name)
    import logging
    from logging import handlers
    log_format = "%(asctime)s[%(levelname)s] - %(name)s[%(funcName)s:%(lineno)d]: %(message)s"
    h_file = handlers.TimedRotatingFileHandler(filename=log_path, when='D', interval=1, backupCount=5, encoding='utf-8')
    h_file.setLevel(logging.INFO)
    h_console = logging.StreamHandler()
    h_console.setLevel(logging.DEBUG)
    logging.basicConfig(handlers=[h_file, h_console], level='DEBUG', datefmt="[%Y-%m-%d %H:%M:%S]", format=log_format)
    logging.getLogger('schedule').level = logging.WARNING
    pass


def get_logger(name):
    logger = logging.getLogger(name)
    return logger


init_logging()


class Utility(object):

    LOGGER = get_logger("game")

    pass


def Logwrap(f, logger):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        # py3 only: def wrapper(*args, depth=None, **kwargs):
        depth = kwargs.pop('depth', None)  # For compatibility with py2
        start = time.time()
        m = inspect.getcallargs(f, *args, **kwargs)
        fndata = {'name': f.__name__, 'call_args': m, 'start_time': start}
        logger.info("invoke. %s", fndata)
        try:
            res = f(*args, **kwargs)
        except Exception as e:
            data = {"traceback": traceback.format_exc(), "end_time": time.time()}
            logger.info("invoke. %s", data)
            raise
        else:
            fndata.update({'ret': res, "end_time": time.time()})
        finally:
            logger.info('function', fndata, depth=depth)
            logger.running_stack.pop()
        return res
    return wrapper
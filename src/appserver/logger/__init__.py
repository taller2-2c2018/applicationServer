import logging

import os


class LoggerFactory(object):
    LOGGING_LEVEL = os.environ.get('LOGGING_LEVEL')
    if not LOGGING_LEVEL:
        LOGGING_LEVEL = 'DEBUG'
    logging.basicConfig(level=LOGGING_LEVEL)

    @staticmethod
    def get_logger(name):
        logging.Formatter(fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

        return logging.getLogger(name)

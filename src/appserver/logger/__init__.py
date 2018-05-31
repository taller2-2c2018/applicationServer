import logging


class LoggerFactory(object):

    logging.basicConfig(level='DEBUG')

    @staticmethod
    def get_logger(name):
        return logging.getLogger(name)

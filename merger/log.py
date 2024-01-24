import logging


def setup_logger(logging_level):
    '''Setup logging.logger'''
    logger = logging.getLogger('merger')
    logger.propagate = False
    logger.setLevel(logging_level)
    ch = logging.StreamHandler()
    ch.setLevel(logging_level)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    return logger

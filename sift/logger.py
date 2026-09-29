import logging

from . import config
#import sift 

def get_logger(name="sift"):# -> logging.Logger:
    config.ensure_app_dir()
    logger = logging.getLogger(name)

    # only add the file handler once, otherwise it will repete every msg
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        handler = logging.FileHandler(config.LOG_PATH, encoding="utf-8")
        formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


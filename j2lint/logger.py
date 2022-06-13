"""logger.py - Creates logger object.
"""
import logging
from logging import handlers
import sys
JINJA2_LOG_FILE = "jinja2-linter.log"

logger = logging.getLogger('')


def add_handler(log, stream_handler, log_level):
    """ defined logging handlers """
    log_format = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    log.setLevel(log_level)
    if not stream_handler:
        file_handler = handlers.RotatingFileHandler(
            JINJA2_LOG_FILE, maxBytes=(1048576 * 5), backupCount=4)
        file_handler.setFormatter(log_format)
        log.addHandler(file_handler)
    else:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(log_format)
        log.addHandler(console_handler)

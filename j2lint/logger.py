"""logger.py - Creates logger object.
"""
import logging
from logging.handlers import RotatingFileHandler
from logging import handlers
import sys
JINJA2_LOG_FILE = "jinja2-linter.log"

logger = logging.getLogger('')

def add_handler(logger, stream_handler, log_level):
    log_format = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    logger.setLevel(log_level)
    if not stream_handler:
        fh = handlers.RotatingFileHandler(
            JINJA2_LOG_FILE, maxBytes=(1048576 * 5), backupCount=4)
        fh.setFormatter(log_format)
        logger.addHandler(fh)
    else:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(log_format)
        logger.addHandler(console_handler)

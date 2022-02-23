"""logger.py - Creates logger object.
"""
import logging
from logging.handlers import RotatingFileHandler
from logging import handlers
import sys
JINJA2_LOG_FILE = "jinja2-linter.log"

logger = logging.getLogger('')

def add_handler(logger, stream=False, stream_level=logging.INFO):
    log_format = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    if not stream:
        fh = handlers.RotatingFileHandler(
            JINJA2_LOG_FILE, maxBytes=(1048576 * 5), backupCount=4)
        fh.setFormatter(log_format)
        logger.setLevel(stream_level)
        logger.addHandler(fh)
    else:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(log_format)
        logger.setLevel(stream_level)
        logger.addHandler(console_handler)

"""logger.py - Creates logger object.
"""
import logging
from logging import handlers

from rich.logging import RichHandler

JINJA2_LOG_FILE = "jinja2-linter.log"

logger = logging.getLogger("")


def add_handler(log: logging.Logger, stream_handler: bool, log_level: int) -> None:
    """defined logging handlers"""
    log_format = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    log.setLevel(log_level)
    if not stream_handler:
        file_handler = handlers.RotatingFileHandler(
            JINJA2_LOG_FILE, maxBytes=(1048576 * 5), backupCount=4
        )
        file_handler.setFormatter(log_format)
        log.addHandler(file_handler)
    else:
        console_handler = RichHandler()
        console_handler.setFormatter(log_format)
        log.addHandler(console_handler)

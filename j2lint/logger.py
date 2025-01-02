# Copyright (c) 2021-2025 Arista Networks, Inc.
# Use of this source code is governed by the MIT license
# that can be found in the LICENSE file.
"""logger.py - Creates logger object."""

import logging
from logging import handlers

from rich.logging import RichHandler

JINJA2_LOG_FILE = "jinja2-linter.log"

logger = logging.getLogger("")


def add_handler(log: logging.Logger, log_level: int, *, stream_handler: bool) -> None:
    """Define logging handlers.

    Parameters
    ----------
    log:
        The logger to manipulate.
    log_level:
        The level to set on `log` as an integer.
    stream_handler:
        When True add a RotatingFileHandler to the logger, otherwise add a RichHandler.
    """
    log_format = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    log.setLevel(log_level)
    if not stream_handler:
        file_handler = handlers.RotatingFileHandler(JINJA2_LOG_FILE, maxBytes=(1048576 * 5), backupCount=4)
        file_handler.setFormatter(log_format)
        log.addHandler(file_handler)
    else:
        console_handler = RichHandler()
        console_handler.setFormatter(log_format)
        log.addHandler(console_handler)

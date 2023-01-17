"""
Tests for j2lint.logger.py
"""
import logging
import sys
from logging import handlers

import pytest
from rich.logging import RichHandler

from j2lint.logger import add_handler


@pytest.mark.parametrize(
    "stream_handler, log_level", [(False, logging.DEBUG), (True, logging.ERROR)]
)
def test_add_handler(logger, stream_handler, log_level):
    """
    Test j2lint.logger.add_handler

    Verify that the correct type of handler is added
    """
    add_handler(logger, stream_handler, log_level)
    logger.setLevel.assert_called_once_with(log_level)
    logger.addHandler.assert_called_once()

    # call_args.args was introduced in Python 3.8
    if sys.version_info >= (3, 8):
        handler_arg = logger.addHandler.call_args.args[0]
    elif sys.version_info >= (3, 6):
        handler_arg = logger.addHandler.call_args[0][0]

    if not stream_handler:
        assert isinstance(handler_arg, handlers.RotatingFileHandler)
    else:
        assert isinstance(handler_arg, RichHandler)

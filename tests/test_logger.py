"""
Tests for j2lint.logger.py
"""
import logging
from logging import handlers
from unittest.mock import create_autospec

import pytest

from j2lint.logger import add_handler


@pytest.fixture
def logger():
    """
    Return a MagicMock object with the spec of logging.Logger
    """
    return create_autospec(logging.Logger)


@pytest.mark.parametrize(
    "stream_handler, log_level", [(False, logging.DEBUG), (True, logging.ERROR)]
)
def test_add_handler(logger, stream_handler, log_level):
    """
    Test j2lint.logger.add_handler
    """
    add_handler(logger, stream_handler, log_level)
    logger.setLevel.assert_called_once_with(log_level)
    logger.addHandler.assert_called_once()
    if not stream_handler:
        assert isinstance(
            logger.addHandler.call_args.args[0], handlers.RotatingFileHandler
        )
    else:
        assert isinstance(logger.addHandler.call_args.args[0], logging.StreamHandler)

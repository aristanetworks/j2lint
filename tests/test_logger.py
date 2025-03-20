# Copyright (c) 2021-2025 Arista Networks, Inc.
# Use of this source code is governed by the MIT license
# that can be found in the LICENSE file.
"""Tests for j2lint.logger.py."""

from __future__ import annotations

import logging
from logging import handlers
from typing import TYPE_CHECKING

import pytest
from rich.logging import RichHandler

from j2lint.logger import add_handler

if TYPE_CHECKING:
    from unittest.mock import MagicMock


@pytest.mark.parametrize(("log_level", "stream_handler"), [(logging.DEBUG, False), (logging.ERROR, True)])
def test_add_handler(logger: MagicMock, log_level: int, *, stream_handler: bool) -> None:
    """Test j2lint.logger.add_handler.

    Verify that the correct type of handler is added
    """
    add_handler(logger, log_level, stream_handler=stream_handler)
    logger.setLevel.assert_called_once_with(log_level)
    logger.addHandler.assert_called_once()

    handler_arg = logger.addHandler.call_args.args[0]

    if not stream_handler:
        assert isinstance(handler_arg, handlers.RotatingFileHandler)
    else:
        assert isinstance(handler_arg, RichHandler)

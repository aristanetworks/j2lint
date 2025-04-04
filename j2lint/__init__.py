# Copyright (c) 2021-2025 Arista Networks, Inc.
# Use of this source code is governed by the MIT license
# that can be found in the LICENSE file.
"""__init__.py - A command-line utility that checks for best practices in Jinja2."""

from rich.console import Console

NAME = "j2lint"
VERSION = "v1.2.0"
DESCRIPTION = __doc__

__author__ = "Arista Networks"
__license__ = "MIT"
__version__ = VERSION

CONSOLE = Console()

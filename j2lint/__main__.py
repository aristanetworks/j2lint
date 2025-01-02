# Copyright (c) 2021-2025 Arista Networks, Inc.
# Use of this source code is governed by the MIT license
# that can be found in the LICENSE file.
"""__main__.py - A command-line utility that checks for best practices in Jinja2."""

import sys

from j2lint import CONSOLE
from j2lint.cli import run

if __name__ == "__main__":
    try:
        sys.exit(run())
    except Exception:  # noqa: BLE001
        CONSOLE.print_exception(show_locals=True)
        raise SystemExit from BaseException

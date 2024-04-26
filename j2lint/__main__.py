#!/usr/bin/python
# Copyright (c) 2021-2024 Arista Networks, Inc.
# Use of this source code is governed by the MIT license
# that can be found in the LICENSE file.
"""__main__.py - A command-line utility that checks for best practices in Jinja2.
"""
import sys
import traceback

from j2lint.cli import run

if __name__ == "__main__":
    try:
        sys.exit(run())
    except Exception:
        print(traceback.format_exc())
        raise SystemExit from BaseException

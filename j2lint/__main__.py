#!/usr/bin/python
import sys

from j2lint.cli import run

if __name__ == "__main__":
    try:
        sys.exit(run())
    except Exception as e:
        raise SystemExit(str(e))

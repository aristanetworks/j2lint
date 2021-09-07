#!/usr/bin/python
import sys
import traceback

from j2lint.cli import run

if __name__ == "__main__":
    try:
        sys.exit(run())
    except Exception as e:
        print(traceback.format_exc())
        raise SystemExit()

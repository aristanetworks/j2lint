"""__main__.py - A command-line utility that checks for best practices in Jinja2.
"""
#!/usr/bin/python
import sys
import traceback

from j2lint.cli import run

if __name__ == "__main__":
    try:
        sys.exit(run())
    except Exception as e:
        print(traceback.format_exc())
        raise SystemExit from BaseException

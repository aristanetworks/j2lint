"""statement.py - Class and variables for jinja statements.
"""
from __future__ import annotations

# pylint: disable=too-few-public-methods
import re

from j2lint.utils import Statement

JINJA_STATEMENT_TAG_NAMES = [
    ("for", "else", "endfor"),
    ("if", "elif", "else", "endif"),
    ("macro", "endmacro"),
]


class JinjaStatement:
    """Class for representing a jinja statement."""

    # pylint: disable = fixme
    # FIXME - this could probably be a method in Node rather than a class
    #         with no method - maybe a dataclass
    def __init__(self, line: Statement) -> None:
        whitespaces = re.findall(r"\s*", line[0])

        self.begin: int = len(whitespaces[0])
        self.line: str = line[0]
        self.words: list[str] = line[0].split()
        self.start_line_no: int = line[1]
        self.end_line_no: int = line[2]
        self.start_delimiter: str = line[3]
        self.end_delimiter: str = line[4]

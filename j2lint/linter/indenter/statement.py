# Copyright (c) 2021-2025 Arista Networks, Inc.
# Use of this source code is governed by the MIT license
# that can be found in the LICENSE file.
"""statement.py - Class and variables for jinja statements."""

from __future__ import annotations

# pylint: disable=too-few-public-methods
import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from j2lint.utils import Statement

JINJA_STATEMENT_TAG_NAMES = [
    ("for", "else", "endfor"),
    ("if", "elif", "else", "endif"),
    ("macro", "endmacro"),
]


class JinjaStatement:
    """Class for representing a jinja statement."""

    # TODO: this could probably be a method in Node rather than a class with no method - maybe a dataclass
    def __init__(self, line: Statement) -> None:
        whitespaces = re.findall(r"\s*", line[0])

        self.begin: int = len(whitespaces[0])
        self.line: str = line[0]
        self.words: list[str] = line[0].split()
        self.start_line_no: int = line[1]
        self.end_line_no: int = line[2]
        self.start_delimiter: str = line[3]
        self.end_delimiter: str = line[4]

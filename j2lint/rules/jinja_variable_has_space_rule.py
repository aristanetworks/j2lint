# Copyright (c) 2021-2024 Arista Networks, Inc.
# Use of this source code is governed by the MIT license
# that can be found in the LICENSE file.
"""jinja_variable_has_space_rule.py - Rule class to check if jinja variables have single space between curly brackets and variable name."""

from __future__ import annotations

import re
from typing import Any

from j2lint.linter.error import LinterError
from j2lint.linter.rule import Rule


class JinjaVariableHasSpaceRule(Rule):
    """Rule class to check if jinja variables have single space between curly brackets and variable name."""

    rule_id = "S1"
    description: ClassVar = "A single space should be added between Jinja2 curly brackets " "and a variable name: {{ ethernet_interface }}"

    short_description = "single-space-decorator"
    severity = "LOW"

    regex = re.compile(r"{{[^ \-\+\d][^}]+}}|{{[-\+][^ ][^}]+}}|{{[^}]+[^ \-\+\d]}}|{{[^}]+[^ {][-\+\d]}}|{{ \s+[^ \-\+]}}|{{[^}]+[^ \-\+] \s+}}")

    def __init__(self, ignore: bool = False, warn: list[Any] | None = None) -> None:
        super().__init__()

    def checktext(self, filename: str, text: str) -> list[LinterError]:
        """Not Implemented for this rule."""
        raise NotImplementedError

    def checkline(self, filename: str, line: str, line_no: int) -> list[LinterError]:
        """
        Check if the given line matches the error regex.

        Parameters
        ----------
        filename
            The filename to which the line belongs.
        line
            The content of the line to check.
        line_no:
            The line number.

        Returns
        -------
        list[LinterError]
            The list of LinterError generated by this rule.
        """
        matches = self.regex.search(line)
        return [LinterError(line_no, line, filename, self)] if matches else []

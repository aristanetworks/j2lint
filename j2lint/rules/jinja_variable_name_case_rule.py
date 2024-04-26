# Copyright (c) 2021-2024 Arista Networks, Inc.
# Use of this source code is governed by the MIT license
# that can be found in the LICENSE file.
"""jinja_variable_name_case_rule.py - Rule class to check the variables use
                                  lower case.
"""
from __future__ import annotations

import re
from typing import Any

from j2lint.linter.error import LinterError
from j2lint.linter.rule import Rule
from j2lint.utils import get_jinja_variables

# pylint: disable=duplicate-code


class JinjaVariableNameCaseRule(Rule):
    """Rule class to check the variables use lower case."""

    rule_id = "V1"
    description = "All variables should use lower case: '{{ variable }}'"
    short_description = "jinja-variable-lower-case"
    severity = "LOW"

    regex = re.compile(r"([a-zA-Z0-9-_\"']*[A-Z][a-zA-Z0-9-_\"']*)")

    def __init__(self, ignore: bool = False, warn: list[Any] | None = None) -> None:
        super().__init__()

    def checktext(self, filename: str, text: str) -> list[LinterError]:
        raise NotImplementedError

    def checkline(self, filename: str, line: str, line_no: int) -> list[LinterError]:
        """
        Checks if the given line matches the error regex, which matches
        variables with non lower case characters

        Args:
            line (string): a single line from the file

        Returns:
            list[LinterError]: the list of LinterError generated by this rule
        """
        variables = get_jinja_variables(line)
        matches = []
        for var in variables:
            matches = re.findall(self.regex, var)
            matches = [
                match
                for match in matches
                if (match not in ["False", "True"])
                and ("'" not in match)
                and ('"' not in match)
            ]

        return [
            LinterError(line_no, line, filename, self, f"{self.description}: {match}")
            for match in matches
        ]

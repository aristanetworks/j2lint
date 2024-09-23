# Copyright (c) 2021-2024 Arista Networks, Inc.
# Use of this source code is governed by the MIT license
# that can be found in the LICENSE file.
"""jinja_operator_has_spaces_rule.py - Rule class to check if operator has surrounding spaces."""

from __future__ import annotations

import re
from typing import Any, ClassVar

from j2lint.linter.error import LinterError
from j2lint.linter.rule import Rule


class JinjaOperatorHasSpacesRule(Rule):
    """Rule class to check if jinja filter has surrounding spaces."""

    rule_id = "S2"
    description = "When variables are used in combination with an operator, the operator should be enclosed by space: '{{ my_value | to_json }}'"
    short_description = "operator-enclosed-by-spaces"
    severity = "LOW"

    # pylint: disable=fixme
    # TODO: make the regex detect the operator position
    operators: ClassVar = ["|", "+", "=="]
    regexes: ClassVar = []
    for operator in operators:
        escaped_operator = "\\" + operator
        regex = (
            r"({[{|%](.*?)([^ |^}]"
            + escaped_operator
            + ")(.*?)[}|%]})|({[{|%](.*?)("
            + escaped_operator
            + r"[^ |^{])(.*?)[}|%]})|({[{|%](.*?)([^ |^}] \s+"
            + escaped_operator
            + ")(.*?)[}|%]})|({[{|%](.*?)("
            + escaped_operator
            + r" \s+[^ |^{])(.*?)[}|%]})"
        )
        regexes.append(re.compile(regex))

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
        errors: list[LinterError] = []
        # TODO: refactor this code removes any single quoted string and any double quoted string to avoid false positive on operators
        if "'" in line:
            regx = re.findall("'([^']*)'", line)
            for match in regx:
                line = line.replace(("'" + match + "'"), "''")

        if '"' in line:
            regx = re.findall('"([^"]*)"', line)
            for match in regx:
                line = line.replace(('"' + match + '"'), '""')

        issues = [operator for regex, operator in zip(self.regexes, self.operators) if regex.search(line)]
        errors.extend(
            LinterError(
                line_no,
                line,
                filename,
                self,
                f"The operator {issue} needs to be enclosed" " by a single space on each side",
            )
            for issue in issues
        )

        return errors

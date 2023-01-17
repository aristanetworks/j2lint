"""jinja_template_syntax_error_rule.py - Rule class to check that file does not
                                     have jinja syntax errors.
"""
from __future__ import annotations

from typing import Any

import jinja2

from j2lint.linter.error import LinterError
from j2lint.linter.rule import Rule


class JinjaTemplateSyntaxErrorRule(Rule):
    """Rule class to check that file does not have jinja syntax errors."""

    rule_id = "S0"
    description = "Jinja syntax should be correct"
    short_description = "jinja-syntax-error"
    severity = "HIGH"

    def __init__(self, ignore: bool = False, warn: list[Any] | None = None) -> None:
        super().__init__()

    def checktext(self, filename: str, text: str) -> list[LinterError]:
        """Checks if the given text has jinja syntax error

        Args:
            file (string): file path
            text (string): entire text content of the file

        Returns:
            list: Returns list of error objects
        """
        result = []

        env = jinja2.Environment(
            extensions=["jinja2.ext.do", "jinja2.ext.loopcontrols"]
        )
        try:
            env.parse(text)
        except jinja2.TemplateSyntaxError as error:
            result.append(
                LinterError(
                    error.lineno,
                    text.split("\n")[error.lineno - 1],
                    filename,
                    self,
                    error.message,
                )
            )

        return result

    def checkline(self, filename: str, line: str, line_no: int) -> list[LinterError]:
        raise NotImplementedError

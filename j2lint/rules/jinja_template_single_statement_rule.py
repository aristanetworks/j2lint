"""jinja_template_single_statement_rule.py - Rule class to check if only a single
                                         jinja statement is present on each
                                         line.
"""
from __future__ import annotations

from j2lint.linter.rule import Rule
from j2lint.utils import get_jinja_statements


class JinjaTemplateSingleStatementRule(Rule):
    """Rule class to check if only a single jinja statement is present on each
    line.
    """

    id = "S7"
    short_description = "single-statement-per-line"
    description = "Jinja statements should be on separate lines"
    severity = "MEDIUM"

    def check(self, line: str) -> bool:
        """Checks if the given line matches the error regex

        Args:
            line (string): a single line from the file

        Returns:
            bool: Returns True if error is found else False
        """
        return len(get_jinja_statements(line)) > 1

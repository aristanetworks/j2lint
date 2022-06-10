"""JinjaStatementDelimiterRule.py - Rule class to check if jinja delimiters
                                    are wrong.
"""
import re
import jinja2
from j2lint.linter.rule import Rule
from j2lint.utils import get_jinja_statements


class JinjaStatementDelimiterRule(Rule):
    """Rule class to check if jinja delimiters are wrong.
    """
    id = 'S6'
    short_description = 'jinja-statements-delimiter'
    description = "Jinja statements should not have {%- or {%+ or -%} as delimiters"
    severity = 'LOW'

    def check(self, file, line):
        """Checks if the given line matches the wrong delimiters

        Args:
            file (string): file path
            line (string): a single line from the file

        Returns:
            Object: Returns True if error is found else False
        """
        statements = get_jinja_statements(line)
        for statement in statements:
            if statement[3] in ["{%-", "{%+"] or statement[4] == "-%}":
                return True
        return False

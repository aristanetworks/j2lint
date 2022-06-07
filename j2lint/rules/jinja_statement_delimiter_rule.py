"""jinja_statement_delimiter_rule.py - Rule class to check if jinja delimiters
                                    are wrong.
"""

from j2lint.linter.rule import Rule
from j2lint.utils import get_jinja_statements


class JinjaStatementDelimiterRule(Rule):
    """Rule class to check if jinja delimiters are wrong.
    """
    id = 'S6'
    # FIXME - for now supporting both syntax for the short_description to be backward
    #         compatible.
    #         The doc and READMEs are fixed to show only the new syntax.
    #         This will be removed
    short_description = 'jinja-statements-delimiter'
    deprecated_short_description = 'jinja-statements-delimeter'
    description = "Jinja statements should not have {%- or {%+ or -%} as delimiters"
    severity = 'LOW'

    def check(self, line):
        """Checks if the given line matches the wrong delimiters

        Args:
            line (string): a single line from the file

        Returns:
            Object: Returns True if error is found else False
        """
        statements = get_jinja_statements(line)
        for statement in statements:
            if statement[3] in ["{%-", "{%+"] or statement[4] == "-%}":
                return True

        return False

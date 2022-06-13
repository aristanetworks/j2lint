"""jinja_statement_has_spaces_rule.py - Rule class to check if jinja statement has
                                        at least a single space surrounding the
                                        delimiter.
"""
import re
from j2lint.linter.rule import Rule


class JinjaStatementHasSpacesRule(Rule):
    """Rule class to check if jinja statement has at least a single space
       surrounding the delimiter.
    """
    id = 'S4'
    short_description = 'jinja-statements-single-space'
    description = "Jinja statement should have a single space before and after: '{% statement %}'"
    severity = 'LOW'

    regex = re.compile(r"{%[^ \-\+]|{%[\-\+][^ ]|[^ \-\+]%}|[^ ][\-\+]%}")

    def check(self, line):
        """Checks if the given line matches the error regex

        Args:
            line (string): a single line from the file

        Returns:
            Object: Returns error object if found else None
        """

        return self.regex.search(line)

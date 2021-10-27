"""JinjaStatementHasSpacesRule.py - Rule class to check if jinja statement has
                                    atleast a single space surrounding the
                                    delimeter.
"""
import re
from j2lint.linter.rule import Rule


class JinjaStatementHasSpacesRule(Rule):
    """Rule class to check if jinja statement has atleast a single space
       surrounding the delimeter.
    """
    id = 'S4'
    short_description = 'jinja-statements-single-space'
    description = "Jinja statement should have a single space before and after: '{% statement %}'"
    severity = 'LOW'

    regex = re.compile(r"{%[^ \-\+]|{%[\-\+][^ ]|[^ \-\+]%}|[^ ][\-\+]%}")

    def check(self, file, line):
        """Checks if the given line matches the error regex

        Args:
            file (string): file path
            line (string): a single line from the file

        Returns:
            Object: Returns error object if found else None
        """
        return self.regex.search(line)

"""JinjaFilterHasSpaceRule.py - Rule class to check if jinja filter has
                                surrounding spaces.
"""
import re
from j2lint.linter.rule import Rule


class JinjaFilterHasSpaceRule(Rule):
    """Rule class to check if jinja filter has surrounding spaces.
    """
    id = 'SYNTAX-2'
    short_description = 'jinja-filter-single-space'
    description = "When variables are used in combination with a filter, | shall be enclosed by space: '{{ my_value | to_json }}'"
    severity = 'LOW'

    regex = re.compile(
        r"({{(.*?)([^ |^}]\|)(.*?)}})|({{(.*?)(\|[^ |^{])(.*?)}})|({{(.*?)([^ |^}] \s+\|)(.*?)}})|({{(.*?)(\| \s+[^ |^{])(.*?)}})")

    def check(self, file, line):
        """Checks if the given line matches the error regex

        Args:
            file (string): file path
            line (string): a single line from the file

        Returns:
            Object: Returns error object if found else None
        """
        return self.regex.search(line)

"""JinjaVariableNameCaseRule.py - Rule class to check the variables use
                                  lower case.
"""
import re
from j2lint.linter.rule import Rule


class JinjaVariableNameCaseRule(Rule):
    """Rule class to check the variables use lower case.
    """
    id = 'VAR-1'
    short_description = 'jinja-variable-lower-case'
    description = "All variables shall use lower case: '{{ variable }}'"
    severity = 'LOW'

    regex = re.compile(r"{{\s*\w*[A-Z]\w*\s*}}")

    def check(self, file, line):
        """Checks if the given line matches the error regex

        Args:
            file (string): file path
            line (string): a single line from the file

        Returns:
            Object: Returns error object if found else None
        """
        return self.regex.search(line)

""" JinjaVariableNameFormatRule.py - Rule class to check that variable names
                                     only use underscores.
"""
import re
from j2lint.linter.rule import Rule


class JinjaVariableNameFormatRule(Rule):
    """Rule class to check that variable names only use underscores.
    """
    id = 'VAR-2'
    short_description = 'jinja-variable-format'
    description = "If variable is multi-words, underscore _ shall be used as a separator: '{{ my_variable_name }}'"
    severity = 'LOW'

    regex = re.compile(r"{{\s*\w*[\-]+\w*\s*}}")

    def check(self, file, line):
        """Checks if the given line matches the error regex

        Args:
            file (string): file path
            line (string): a single line from the file

        Returns:
            Object: Returns error object if found else None
        """
        return self.regex.search(line)

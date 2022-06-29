""" jinja_variable_name_format_rule.py - Rule class to check that variable names
                                     only use underscores.
"""
import re
from j2lint.linter.rule import Rule
from j2lint.utils import get_jinja_variables


class JinjaVariableNameFormatRule(Rule):
    """Rule class to check that variable names only use underscores.
    """
    id = 'V2'
    short_description = 'jinja-variable-format'
    description = ("If variable is multi-words, underscore _ shall be used "
                   "as a separator: '{{ my_variable_name }}'")
    severity = 'LOW'

    regex = re.compile(r"[a-zA-Z0-9-_\"']+[-][a-zA-Z0-9-_\"']+")

    def check(self, line):
        """Checks if the given line matches the error regex

        Args:
            line (string): a single line from the file

        Returns:
            Object: Returns error object if found else None
        """
        variables = get_jinja_variables(line)
        for var in variables:
            matches = re.findall(self.regex, var)
            matches = [match for match in matches if (
                "'" not in match) and ('"' not in match)]
            if matches:
                return True

        return False

"""jinja_variable_name_case_rule.py - Rule class to check the variables use
                                  lower case.
"""
import re
from j2lint.linter.rule import Rule
from j2lint.utils import get_jinja_variables


class JinjaVariableNameCaseRule(Rule):
    """Rule class to check the variables use lower case.
    """
    id = 'V1'
    short_description = 'jinja-variable-lower-case'
    description = "All variables shall use lower case: '{{ variable }}'"
    severity = 'LOW'

    regex = re.compile(r"([a-zA-Z0-9-_\"']*[A-Z][a-zA-Z0-9-_\"']*)")

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
            matches = [match for match in matches if (match not in ['False', 'True']) and (
                "'" not in match) and ('"' not in match)]
            if matches:
                return True

        return False

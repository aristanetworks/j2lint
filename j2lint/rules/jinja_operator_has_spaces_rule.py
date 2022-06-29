"""jinja_operator_has_spaces_rule.py - Rule class to check if operator has
                                  surrounding spaces.
"""
import re
from j2lint.linter.rule import Rule


class JinjaOperatorHasSpacesRule(Rule):
    """Rule class to check if jinja filter has surrounding spaces.
    """
    id = 'S2'
    short_description = 'operator-enclosed-by-spaces'
    description = ("When variables are used in combination with an operator, "
                   "the operator shall be enclosed by space: '{{ my_value | to_json }}'")
    severity = 'LOW'

    operators = ['|', '+', '==']
    regexes = []
    for operator in operators:
        operator = "\\" + operator
        regex = (r"({[{|%](.*?)([^ |^}]" + operator + ")(.*?)[}|%]})|({[{|%](.*?)(" + operator +
                 r"[^ |^{])(.*?)[}|%]})|({[{|%](.*?)([^ |^}] \s+" + operator +
                 ")(.*?)[}|%]})|({[{|%](.*?)(" +
                 operator + r" \s+[^ |^{])(.*?)[}|%]})")
        regexes.append(re.compile(regex))

    def check(self, line):
        """Checks if the given line matches the error regex

        Args:
            line (string): a single line from the file

        Returns:
            Object: Returns error object if found else None
        """
        issues = []

        if "\'" in line:
            regx = re.findall("\'([^\']*)\'", line)
            for match in regx:
                line = line.replace(("\'" + match + "\'"), "''")

        if "\"" in line:
            regx = re.findall("\"([^\"]*)\"", line)
            for match in regx:
                line = line.replace(("\"" + match + "\""), '""')

        # pylint: disable = fixme
        # FIXME - be able to detect multiple times the same operator
        for (regex, operator) in zip(self.regexes, self.operators):
            if regex.search(line):
                issues.append(operator)
        if issues:
            if len(issues) > 1:
                self.description = (f"The operators {(', '.join(issues))} need to be enclosed "
                                    "by a single space on each side")
            else:
                self.description = (f"The operator {(', '.join(issues))} needs to be enclosed"
                                    " by a single space on each side")
            return True

        return False

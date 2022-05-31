"""JinjaOperatorHasSpaceRule.py - Rule class to check if operator has
                                  surrounding spaces.
"""
import re
from j2lint.linter.rule import Rule


class JinjaOperatorHasSpaceRule(Rule):
    """Rule class to check if jinja filter has surrounding spaces.
    """
    id = 'S2'
    short_description = 'operator-enclosed-by-spaces'
    description = "When variables are used in combination with an operator, the operator shall be enclosed by space: '{{ my_value | to_json }}'"
    severity = 'LOW'

    operators = ['|', '+', '==']
    regexes = []
    for operator in operators:
        operator = "\\" + operator
        regex = r"({[{|%](.*?)([^ |^}]" + operator + ")(.*?)[}|%]})|({[{|%](.*?)(" + operator + \
            "[^ |^{])(.*?)[}|%]})|({[{|%](.*?)([^ |^}] \s+" + operator + \
            ")(.*?)[}|%]})|({[{|%](.*?)(" + \
            operator + " \s+[^ |^{])(.*?)[}|%]})"
        regexes.append(re.compile(regex))

    def check(self, file, line):
        """Checks if the given line matches the error regex

        Args:
            file (string): file path
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

        for (regex, operator) in zip(self.regexes, self.operators):
            if regex.search(line):
                issues.append(operator)
        if issues:
            if len(issues) > 1:
                self.description = "The operators %s need to be enclosed by a single space on each side" % (
                    ", ".join(issues))
            else:
                self.description = "The operator %s needs to be enclosed by a single space on each side" % (
                    ", ".join(issues))
            return True
        return False

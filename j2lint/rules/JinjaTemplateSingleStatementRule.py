import re
import jinja2
from j2lint.linter.rule import Rule


class JinjaTemplateSingleStatementRule(Rule):
    id = 'SYNTAX-3-4'
    description = "Jinja statements should be on separate lines"
    severity = 'HIGH'

    regex = re.compile(r"{%")

    def match(self, file, line):
        if len(self.regex.findall(line)) > 1:
            return True
        return False

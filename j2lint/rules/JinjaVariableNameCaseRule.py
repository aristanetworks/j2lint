import re
from j2lint.linter.rule import Rule


class JinjaVariableNameCaseRule(Rule):
    id = 'VAR-1'
    short_description = 'jinja-variable-lower-case'
    description = "All variables shall use lower case: '{{ variable }}'"
    severity = 'LOW'

    regex = re.compile(r"{{\s*\w*[A-Z]\w*\s*}}")

    def match(self, file, line):
        return self.regex.search(line)

import re
from j2lint.linter.rule import Rule


class JinjaVariableNameFormatRule(Rule):
    id = 'VAR-2'
    description = "Jinja variables shall use underscore _ as a separator if it has multiple words: '{{ my_variable_name }}'"
    severity = 'LOW'

    regex = re.compile(r"{{\s*\w*[\-]+\w*\s*}}")

    def match(self, file, line):
        return self.regex.search(line)

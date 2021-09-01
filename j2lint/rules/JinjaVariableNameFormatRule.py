import re
from j2lint.linter.rule import Rule


class JinjaVariableNameFormatRule(Rule):
    id = 'VAR-2'
    description = "If variable is multi-words, underscore _ shall be used as a separator: '{{ my_variable_name }}'"
    severity = 'LOW'

    regex = re.compile(r"{{\s*\w*[\-]+\w*\s*}}")

    def match(self, file, line):
        return self.regex.search(line)

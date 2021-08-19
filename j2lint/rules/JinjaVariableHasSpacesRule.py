import re
from j2lint.linter.rule import Rule


class JinjaVariableHasSpacesRule(Rule):
    id = 'SYNTAX1'
    description = "Jinja variables should have a single space before and after: '{{ var_name }}'"
    severity = 'LOW'

    regex = re.compile(
        r"{{[^ \-\+\d]|{{[-\+][^ ]|[^ \-\+\d]}}|[^ {][-\+\d]}}|{{ \s+[^ \-\+]|[^ \-\+] \s+}}")

    def match(self, file, line):
        return self.regex.search(line)

import re
from j2lint.linter.rule import Rule


class JinjaVariableHasSpacesRule(Rule):
    id = 'SYNTAX-1'
    description = "Jinja variables should have a single space between Jinja2 curly brackets and variable's name: '{{ var_name }}'"
    severity = 'LOW'

    regex = re.compile(
        r"{{[^ \-\+\d]|{{[-\+][^ ]|[^ \-\+\d]}}|[^ {][-\+\d]}}|{{ \s+[^ \-\+]|[^ \-\+] \s+}}")

    def match(self, file, line):
        return self.regex.search(line)

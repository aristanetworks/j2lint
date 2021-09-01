import re
from j2lint.linter.rule import Rule


class JinjaVariableHasSpaceRule(Rule):
    id = 'SYNTAX-1'
    description = "A single space shall be added between Jinja2 curly brackets and a variable’s name: '{{ ethernet_interface }}'"
    severity = 'LOW'

    regex = re.compile(
        r"{{[^ \-\+\d]|{{[-\+][^ ]|[^ \-\+\d]}}|[^ {][-\+\d]}}|{{ \s+[^ \-\+]|[^ \-\+] \s+}}")

    def match(self, file, line):
        return self.regex.search(line)

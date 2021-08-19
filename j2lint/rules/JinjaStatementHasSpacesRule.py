import re
from j2lint.linter.rule import Rule


class JinjaStatementHasSpacesRule(Rule):
    id = 'SYNTAX2'
    description = "Jinja statement should have a single space before and after: '{% statement %}'"
    severity = 'LOW'

    regex = re.compile(
        r"{%+[^ \-\+]|{%[\-\+][^ ]|[^ \-\+]%}|[^ ][\-\+]%}|{% \s+[^ \-\+]|[^ \-\+] \s+%}")

    def match(self, file, line):
        return self.regex.search(line)

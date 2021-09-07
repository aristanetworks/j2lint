import re
from j2lint.linter.rule import Rule


class JinjaStatementHasSpacesRule(Rule):
    id = 'SYNTAX-3-1'
    short_description = 'jinja-statement-single-space'
    description = "Jinja statement should have a single space before and after: '{% statement %}'"
    severity = 'LOW'

    regex = re.compile(r"{%[^ \-\+]|{%[\-\+][^ ]|[^ \-\+]%}|[^ ][\-\+]%}")

    def match(self, file, line):
        return self.regex.search(line)

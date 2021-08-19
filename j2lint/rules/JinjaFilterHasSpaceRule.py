import re
from j2lint.linter.rule import Rule


class JinjaFilterHasSpaceRule(Rule):
    id = 'SYNTAX3'
    description = "Jinja filter should have a single space before and after: '{{ var_name | filter }}'"
    severity = 'LOW'

    regex = re.compile(r"([^ ]\|)|(\|[^ ])|([^ ] \s+\|)|(\| \s+[^ ])")

    def match(self, file, line):
        return self.regex.search(line)

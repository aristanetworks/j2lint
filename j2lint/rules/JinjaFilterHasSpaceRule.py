import re
from j2lint.linter.rule import Rule


class JinjaFilterHasSpaceRule(Rule):
    id = 'SYNTAX-2'
    description = "When variables are used in combination with a filter, | shall be enclosed by space: '{{ my_value | to_json }}'"
    severity = 'LOW'

    regex = re.compile(r"([^ ]\|)|(\|[^ ])|([^ ] \s+\|)|(\| \s+[^ ])")

    def match(self, file, line):
        return self.regex.search(line)

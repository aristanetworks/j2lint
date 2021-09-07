import re
import jinja2
from j2lint.linter.rule import Rule


class JinjaTemplateNoTabsRule(Rule):
    id = 'SYNTAX-3-3'
    short_description = 'no-tabs'
    description = "Indentation are 4 spaces and NOT tabulation"
    severity = 'LOW'

    regex = re.compile(r"\t+")

    def match(self, file, line):
        return self.regex.search(line)

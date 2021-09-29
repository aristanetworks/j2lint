"""JinjaTemplateNoTabsRule.py - Rule class to check the file does not use tabs
                                for indentation.
"""
import re
import jinja2
from j2lint.linter.rule import Rule


class JinjaTemplateNoTabsRule(Rule):
    """Rule class to check the file does not use tabs for indentation.
    """
    id = 'S3-3'
    short_description = 'no-tabs'
    description = "Indentation are 4 spaces and NOT tabulation"
    severity = 'LOW'

    regex = re.compile(r"\t+")

    def check(self, file, line):
        """Checks if the given line matches the error regex

        Args:
            file (string): file path
            line (string): a single line from the file

        Returns:
            Object: Returns error object if found else None
        """
        return self.regex.search(line)

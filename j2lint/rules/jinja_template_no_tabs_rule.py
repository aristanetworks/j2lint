"""jinja_template_no_tabs_rule.py - Rule class to check the file does not use tabs
                                for indentation.
"""
import re
from j2lint.linter.rule import Rule
from j2lint.logger import logger


class JinjaTemplateNoTabsRule(Rule):
    """Rule class to check the file does not use tabs for indentation.
    """
    id = 'S5'
    short_description = 'jinja-statements-no-tabs'
    description = "Indentation are 4 spaces and NOT tabulation"
    severity = 'LOW'

    regex = re.compile(r"\t+")

    def check(self, line):
        """Checks if the given line matches the error regex

        Args:
            line (string): a single line from the file

        Returns:
            Object: Returns error object if found else None
        """

        logger.debug("Check line rule does not exist for %s",
                     __class__.__name__)

        return self.regex.search(line)

"""JinjaVariableHasSpaceRule.py - Rule class to check if jinja variables have
                                  single space between curly brackets and
                                  variable name.
"""
import re
from j2lint.linter.rule import Rule
from j2lint.logger import logger


class JinjaVariableHasSpaceRule(Rule):
    """Rule class to check if jinja variables have single space between curly
       brackets and variable name.
    """
    id = 'S1'
    short_description = 'single-space-decorator'
    description = "A single space shall be added between Jinja2 curly brackets" \
                  " and a variable’s name: "'{{ ethernet_interface }}'
    severity = 'LOW'

    regex = re.compile(
        r"{{[^ \-\+\d]|{{[-\+][^ ]|[^ \-\+\d]}}|[^ {][-\+\d]}}|{{ \s+[^ \-\+]|[^ \-\+] \s+}}")

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

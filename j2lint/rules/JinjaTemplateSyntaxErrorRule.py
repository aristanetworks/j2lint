"""JinjaTemplateSyntaxErrorRule.py - Rule class to check that file does not
                                     have jinja syntax errors.
"""
import re
import jinja2
from j2lint.linter.rule import Rule


class JinjaTemplateSyntaxErrorRule(Rule):
    """Rule class to check that file does not have jinja syntax errors.
    """
    id = 'SYNTAX-0'
    short_description = 'syntax-error'
    description = "Jinja syntax should be correct"
    severity = 'HIGH'

    def checktext(self, file, text):
        """Checks if the given text has jinja syntax error

        Args:
            file (string): file path
            text (string): entire text content of the file

        Returns:
            list: Returns list of error objects
        """
        result = []

        env = jinja2.Environment(
            extensions=['jinja2.ext.do', 'jinja2.ext.loopcontrols'])
        with open(file['path']) as template:
            try:
                # Try to read the contents of the file as jinja2
                block = template.read()
                env.parse(block)
            except jinja2.TemplateSyntaxError as e:
                result.append((e.lineno, text.split(
                    "\n")[e.lineno - 1], e.message))
        return result

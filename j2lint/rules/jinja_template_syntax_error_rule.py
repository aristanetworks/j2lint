"""jinja_template_syntax_error_rule.py - Rule class to check that file does not
                                     have jinja syntax errors.
"""
import jinja2
from j2lint.linter.rule import Rule


class JinjaTemplateSyntaxErrorRule(Rule):
    """Rule class to check that file does not have jinja syntax errors.
    """
    id = 'S0'
    short_description = 'jinja-syntax-error'
    description = "Jinja syntax should be correct"
    severity = 'HIGH'

    @classmethod
    def checktext(cls, file, text):
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
        with open(file['path'], encoding="utf-8") as template:
            try:
                # Try to read the contents of the file as jinja2
                block = template.read()
                env.parse(block)
            except jinja2.TemplateSyntaxError as error:
                result.append((error.lineno, text.split(
                    "\n")[error.lineno - 1], error.message))

        return result

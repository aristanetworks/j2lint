"""jinja_template_indentation_rule.py - Rule class to check the jinja statement
                                     indentation is correct.
"""
from j2lint.linter.rule import Rule
from j2lint.linter.indenter.node import Node
from j2lint.utils import get_jinja_statements
from j2lint.logger import logger


class JinjaTemplateIndentationRule(Rule):
    """Rule class to check the jinja statement indentation is correct.
    """

    id = 'S3'
    short_description = 'jinja-statements-indentation'
    description = ("All J2 statements must be indented by 4 more spaces within jinja delimiter. "
                  "To close a control, end tag must have same indentation level.")
    severity = 'HIGH'

    @classmethod
    def checktext(cls, file, text):
        """Checks if the given text has the error

        Args:
            file (string): file path
            text (string): entire text content of the file

        Returns:
            list: Returns list of error objects
        """
        result = []
        errors = []

        with open(file['path'], encoding="utf-8") as template:
            text = template.read()
            # Collect only Jinja Statements within delimiters {% and %}
            # and ignore the other statements
            lines = get_jinja_statements(text, indentation=True)

            # Build a tree out of Jinja Statements to get the expected
            # indentation level for each statement
            root = Node()
            try:
                root.check_indentation(errors, lines, 0)
            except SyntaxError as error:
                logger.error("Indentation check failed for file %s: Error: %s",
                             file['path'], str(error))
            for error in errors:
                result.append((error[0], error[1], error[2]))

        logger.debug("Check line rule does not exist for %s",
            __class__.__name__)

        return result

"""JinjaTemplateIndentationRule.py - Rule class to check the jinja statement
                                     indentation is correct.
"""
import re
import jinja2
from j2lint.linter.rule import Rule
from j2lint.linter.indenter.node import Node
from j2lint.utils import get_jinja_statements


class JinjaTemplateIndentationRule(Rule):
    """Rule class to check the jinja statement indentation is correct.
    """
    id = 'S3-2'
    short_description = 'jinja-statements-indentation'
    description = "All J2 statements must be indented by 4 more spaces within jinja delimiter. To close a control, end tag must have same indentation level."
    severity = 'HIGH'

    def checktext(self, file, text):
        """Checks if the given text has the error

        Args:
            file (string): file path
            text (string): entire text content of the file

        Returns:
            list: Returns list of error objects
        """
        result = []
        errors = []
        statements = []

        with open(file['path']) as template:
            text = template.read()
            # Collect only Jinja Statements within delimeters {% and %} and ignore the other statements
            lines = get_jinja_statements(text)

            # Build a tree out of Jinja Statements to get the expected indentation level for each statement
            root = Node()
            try:
                root.check_indentation(errors, lines, 0)
            except Exception as e:
                print("Indentation check failed for file %s: Error: %s" %
                      (file['path'], str(e)))
            for error in errors:
                result.append((error[0], error[1], error[2]))

        return result

import re
import jinja2
from j2lint.linter.rule import Rule
from j2lint.linter.indenter.node import Node
from j2lint.utils import get_jinja_statements


class JinjaTemplateIndentationRule(Rule):
    id = 'SYNTAX-3-2'
    short_description = 'bad-indent'
    description = "All J2 statements must be indented by 4 more spaces within jinja delimiter. To close a control, end tag must have same indentation level."
    severity = 'HIGH'

    def matchtext(self, file, text):
        result = []
        errors = []
        statements = []

        with open(file['path']) as template:
            text = template.read()
            # Collect only Jinja Statements within delimeters {% and %} and ignore the other statements
            lines = get_jinja_statements(text)

            # Build a tree out of Jinja Statements to get the expected indentation level for each statement
            root = Node()
            root.check_indentation(errors, lines, 0)
            for error in errors:
                result.append((error[0], error[1], error[2]))

        return result

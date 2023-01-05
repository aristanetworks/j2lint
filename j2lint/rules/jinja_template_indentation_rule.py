"""jinja_template_indentation_rule.py - Rule class to check the jinja statement
                                     indentation is correct.
"""
from __future__ import annotations

from typing import Any

from j2lint.linter.error import JinjaLinterError
from j2lint.linter.indenter.node import Node, NodeIndentationError
from j2lint.linter.rule import Rule
from j2lint.logger import logger
from j2lint.utils import get_jinja_statements


class JinjaTemplateIndentationRule(Rule):
    """Rule class to check the jinja statement indentation is correct."""

    id = "S3"
    short_description = "jinja-statements-indentation"
    description = (
        "All J2 statements must be indented by 4 more spaces within jinja delimiter. "
        "To close a control, end tag must have same indentation level."
    )
    severity = "HIGH"

    def checktext(self, file: dict[str, Any], text: str) -> list[NodeIndentationError]:
        """Checks if the given text has the error

        Args:
            file (string): file path
            text (string): entire text content of the file

        Returns:
            list: Returns list of error objects
        """
        errors: list[NodeIndentationError] = []
        with open(file["path"], encoding="utf-8") as template:
            text = template.read()
            # Collect only Jinja Statements within delimiters {% and %}
            # and ignore the other statements
            lines = get_jinja_statements(text, indentation=True)

            # Build a tree out of Jinja Statements to get the expected
            # indentation level for each statement
            root = Node()
            try:
                root.check_indentation(errors, lines, 0)
            except (JinjaLinterError, IndexError) as exc:
                logger.error(
                    "Indentation check failed for file %s: Error: %s",
                    file["path"],
                    str(exc),
                )

        return errors

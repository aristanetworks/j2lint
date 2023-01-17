"""jinja_template_indentation_rule.py - Rule class to check the jinja statement
                                     indentation is correct.
"""
from __future__ import annotations

from typing import Any

from j2lint.linter.error import JinjaLinterError, LinterError
from j2lint.linter.indenter.node import Node, NodeIndentationError
from j2lint.linter.rule import Rule
from j2lint.logger import logger
from j2lint.utils import get_jinja_statements


class JinjaTemplateIndentationRule(Rule):
    """Rule class to check the jinja statement indentation is correct."""

    short_description = "jinja-statements-indentation"
    rule_id = "S3"
    description = (
        "All J2 statements must be indented by 4 more spaces within jinja delimiter. "
        "To close a control, end tag must have same indentation level."
    )
    severity = "HIGH"

    def __init__(self, ignore: bool = False, warn: list[Any] | None = None) -> None:
        super().__init__()

    def checktext(self, filename: str, text: str) -> list[LinterError]:
        """Checks if the given text has the error

        Args:
            file (string): file path
            text (string): entire text content of the file

        Returns:
            list: Returns list of error objects
        """
        # Collect only Jinja Statements within delimiters {% and %}
        # and ignore the other statements
        lines = get_jinja_statements(text, indentation=True)

        # Build a tree out of Jinja Statements to get the expected
        # indentation level for each statement
        root = Node()
        node_errors: list[NodeIndentationError] = []
        try:
            root.check_indentation(node_errors, lines, 0)

        # pylint: disable=fixme
        # TODO need to fix this index error in Node
        except (JinjaLinterError, IndexError) as exc:
            logger.error(
                "Indentation check failed for file %s: Error: %s",
                filename,
                str(exc),
            )

        return [
            LinterError(line_no, section, filename, self, message)
            for line_no, section, message in node_errors
        ]

    def checkline(self, filename: str, line: str, line_no: int) -> list[LinterError]:
        raise NotImplementedError

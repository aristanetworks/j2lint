"""error.py - Error classes to format the lint errors.
"""
from __future__ import annotations

import json
from typing import TYPE_CHECKING

from rich.text import Text

from j2lint.logger import logger

if TYPE_CHECKING:
    from .rule import Rule


class LinterError:
    """Class for lint errors."""

    def __init__(
        self,
        line_number: int,
        line: str,
        filename: str,
        rule: Rule,
        message: str | None = None,
    ) -> None:
        # pylint: disable=too-many-arguments
        self.line_number = line_number
        self.line = line
        self.filename = filename
        self.rule = rule
        self.message = message or rule.description

    def to_rich(self, verbose: bool = False) -> Text:
        """setting string output format"""
        text = Text()
        if not verbose:
            text.append(self.filename, "green")
            text.append(":")
            text.append(str(self.line_number), "red")
            text.append(f" {self.message}")
            text.append(f" ({self.rule.short_description})", "blue")
        else:
            logger.debug("Verbose mode enabled")
            text.append("Linting rule: ")
            text.append(f"{self.rule.rule_id}\n", "blue")
            text.append("Rule description: ")
            text.append(f"{self.rule.description}\n", "blue")
            text.append("Error line: ")
            text.append(self.filename, "green")
            text.append(":")
            text.append(str(self.line_number), "red")
            text.append(f" {self.line}\n")
            text.append("Error message: ")
            text.append(f"{self.message}\n")
        return text

    def to_json(self) -> str:
        """setting json output format"""
        return json.dumps(
            {
                "id": self.rule.rule_id,
                "message": self.message,
                "filename": self.filename,
                "line_number": self.line_number,
                "line": self.line,
                "severity": self.rule.severity,
            }
        )


class JinjaLinterError(Exception):
    """Jinja Linter Error"""

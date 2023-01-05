"""error.py - Error classes to format the lint errors.
"""
from __future__ import annotations

import json
from typing import TYPE_CHECKING

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

    def to_string(self, verbose: bool = False) -> str:
        """setting string output format"""
        if not verbose:
            format_str = "{2}:{3} {5} ({6})"
        else:
            logger.debug("Verbose mode enabled")
            format_str = (
                "Linting rule: {0}\nRule description: "
                "{1}\nError line: {2}:{3} {4}\nError message: {5}\n"
            )
        return format_str.format(
            self.rule.id,
            self.rule.description,
            self.filename,
            self.line_number,
            self.line,
            self.message,
            self.rule.short_description,
        )

    def to_json(self) -> str:
        """setting json output format"""
        return json.dumps(
            {
                "id": self.rule.id,
                "message": self.message,
                "filename": self.filename,
                "line_number": self.line_number,
                "line": self.line,
                "severity": self.rule.severity,
            }
        )


class JinjaLinterError(Exception):
    """Jinja Linter Error"""

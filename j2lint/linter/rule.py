"""rule.py - Base class for all the lint rules with functions for mathching
             line and text based rule.
"""
from __future__ import annotations

from typing import Any

from j2lint.linter.error import LinterError
from j2lint.logger import logger
from j2lint.utils import is_valid_file_type


class Rule:
    """Rule class which acts as a base class for rules with regex match
    functions.
    """

    id: str = "G0"  # Default rule G0 as in Generic 0 - should never be used
    description: str | None = None
    short_description: str | None = None
    severity: str | None = None
    ignore: bool = False
    warn: list[Any] = []

    def __repr__(self) -> str:
        return f"{self.id}: {self.description}"

    def checktext(self, file: dict[str, Any], text: str) -> list[Any]:
        """This method is expected to be overriden by child classes"""
        # pylint: disable=unused-argument
        return []

    def check(self, line: str) -> Any:
        """This method is expected to be overriden by child classes"""
        # pylint: disable=unused-argument

    @staticmethod
    def is_valid_language(file: dict[str, Any]) -> bool:
        """Check if the file is a valid Jinja file

        Args:
            file (dict): file path

        Returns:
            bool: True if file extension is correct

        TODO: refactor to use the j2lint.utils.is_valid_language
        """
        return is_valid_file_type(file["path"])

    def checklines(self, file: dict[str, Any], text: str) -> list[LinterError]:
        """Checks each line of file against the error regex

        Args:
            file (string): file path of the file to be checked
            text (string): file text of the same file

        Returns:
            list: list of LinterError from issues in the given file
        """
        errors: list[LinterError] = []

        if not self.is_valid_language(file):
            logger.debug(
                "Skipping file %s. Linter does not support linting this file type", file
            )
            return errors

        for (index, line) in enumerate(text.split("\n")):
            # pylint: disable = fixme
            # FIXME - parsing jinja2 templates .. lines starting with `#
            #         should probably still be parsed somewhow as these
            #         are not comments.
            if line.lstrip().startswith("#"):
                continue

            if self.check(line):
                errors.append(LinterError(index + 1, line, file["path"], self))
        return errors

    def checkfulltext(self, file: dict[str, Any], text: str) -> list[LinterError]:
        """Checks the entire file text against a lint rule

        Args:
            file (string): file path of the file to be checked
            text (string): file text of the same file

        Returns:
            list: list of LinterError from issues in the given file
        """
        errors: list[LinterError] = []

        if not self.is_valid_language(file):
            logger.debug(
                "Skipping file %s. Linter does not support linting this file type", file
            )
            return errors

        results = self.checktext(file, text)

        errors.extend(
            LinterError(line, section, file["path"], self, message)
            for line, section, message in results
        )

        return errors

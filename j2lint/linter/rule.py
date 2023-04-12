"""rule.py - Base class for all the lint rules with functions for mathching
             line and text based rule.
"""
from __future__ import annotations

import json
from abc import ABC, abstractclassmethod, abstractmethod
from typing import Any

from rich.text import Text

from j2lint.linter.error import JinjaLinterError, LinterError
from j2lint.logger import logger
from j2lint.utils import is_valid_file_type


class Rule(ABC):
    """Abstract rule class which acts as a base class for rules with regex match
    functions.
    """

    def __init__(
        self,
        ignore: bool = False,
        warn: list[Any] | None = None,
        origin: str = "BUILT-IN",
    ):
        self.ignore = ignore
        self.warn = warn if warn is not None else []
        self.origin = origin

    # Mandatory class attributes

    # ignoring mypy issue as the BDFL said
    # https://github.com/python/mypy/issues/1362
    @property  # type: ignore
    @abstractclassmethod
    def rule_id(cls) -> str:  # sourcery skip: instance-method-first-arg-name
        """
        The rule id like S0
        """

    @property  # type: ignore
    @abstractclassmethod
    def description(cls) -> str:  # sourcery skip: instance-method-first-arg-name
        """
        The rule description
        """

    @property  # type: ignore
    @abstractclassmethod
    def short_description(cls) -> str:
        # sourcery skip: instance-method-first-arg-name
        """
        The rule short_description
        """

    @property  # type: ignore
    @abstractclassmethod
    def severity(cls) -> str:  # sourcery skip: instance-method-first-arg-name
        """
        The rule severity
        """

    def __init_subclass__(cls, *args: Any, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        if cls.severity not in [None, "LOW", "MEDIUM", "HIGH"]:
            raise JinjaLinterError(
                f"Rule {cls.rule_id}: severity must be in [None, 'LOW', 'MEDIUM', 'HIGH'], {cls.severity} was provided"
            )

    def __repr__(self) -> str:
        return f"{self.rule_id}: {self.description}"

    def to_rich(self) -> Text:
        """
        Return a rich reprsentation of the rule, e.g.:
            S0 Jinja syntax should be correct (jinja-syntax-error)

        Where `S0` is in red and `(jinja-syntax-error)` in blue
        """
        res = Text()
        res.append(f"{self.rule_id} ", "red")
        res.append(self.description)
        res.append(f" ({self.short_description})", "blue")
        return res

    def to_json(self) -> str:
        """Return a json representation of the rule"""
        return json.dumps(
            {
                "rule_id": self.rule_id,
                "short_description": self.short_description,
                "description": self.description,
                "severity": self.severity,
                "origin": self.origin,
            }
        )

    @abstractmethod
    def checktext(self, filename: str, text: str) -> list[LinterError]:
        """This method is expected to be overriden by child classes"""

    @abstractmethod
    def checkline(self, filename: str, line: str, line_no: int) -> list[LinterError]:
        """This method is expected to be overriden by child classes"""

    def checkrule(self, file: dict[str, Any], text: str) -> list[LinterError]:
        """
        Checks the string text against the current rule by calling
        either the checkline or checktext method depending on which one is implemented

        Args:
            file (string): file path of the file to be checked
            text (string): file text of the same file

        Returns:
            list: list of LinterError from issues in the given file
        """
        errors: list[LinterError] = []

        if not is_valid_file_type(file["path"]):
            logger.debug(
                "Skipping file %s. Linter does not support linting this file type", file
            )
            return errors

        try:
            # First try with checktext
            results = self.checktext(file["path"], text)
            errors.extend(results)

        except NotImplementedError:
            # checkline it is
            for index, line in enumerate(text.split("\n")):
                # pylint: disable = fixme
                # FIXME - parsing jinja2 templates .. lines starting with `#
                #         should probably still be parsed somewhow as these
                #         are not comments.
                if line.lstrip().startswith("#"):
                    continue

                results = self.checkline(file["path"], line, line_no=index + 1)
                errors.extend(results)
                # errors.append(LinterError(index + 1, line, file["path"], self))
        return errors

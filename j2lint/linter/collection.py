# Copyright (c) 2021-2025 Arista Networks, Inc.
# Use of this source code is governed by the MIT license
# that can be found in the LICENSE file.
"""collection.py - Class to create a collection of linting rules."""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING

from rich.console import Group
from rich.tree import Tree

from j2lint.linter.error import JinjaLinterError
from j2lint.logger import logger
from j2lint.utils import is_rule_disabled, load_plugins

if TYPE_CHECKING:
    from collections.abc import Iterator

    from .error import LinterError
    from .rule import Rule

DEFAULT_RULE_DIR = Path(__file__).parent.parent / "rules"


class RulesCollection:
    """RulesCollection class which checks the linting rules against a file."""

    def __init__(self, *, verbose: bool = False) -> None:
        self.rules: list[Rule] = []
        self.verbose = verbose

    def __iter__(self) -> Iterator[Rule]:
        """Return iterable of Rules in the collection.

        Returns
        -------
        Iterable[Rule]
        """
        return iter(self.rules)

    def __len__(self) -> int:
        """Return the number of rules in the collection.

        Returns
        -------
        int
            The number of rules in the collection.
        """
        return len(self.rules)

    def extend(self, more: list[Rule]) -> None:
        """Extend list of rules.

        TODO: This does not protect against duplicate rules

        Parameters
        ----------
        more
            List of rules classes to append to the collection.
        """
        self.rules.extend(more)

    def run(self, file_path: Path) -> tuple[list[LinterError], list[LinterError]]:
        """Run the linting rules for given file.

        Parameters
        ----------
        file_path
            Path

        Returns
        -------
        tuple[list, list]
            A tuple containing the list of linting errors and the list of linting warnings found.
        """
        text = ""
        errors: list[LinterError] = []
        warnings: list[LinterError] = []

        try:
            with file_path.open(encoding="utf-8") as file:
                text = file.read()
        except OSError as err:
            logger.warning("Could not open %s - %s", file_path, err.strerror)
            return errors, warnings

        for rule in self.rules:
            if rule.ignore:
                logger.debug(
                    "Ignoring rule %s:%s for file %s",
                    rule.rule_id,
                    rule.short_description,
                    file_path,
                )
                continue
            if is_rule_disabled(text, rule):
                logger.debug("Skipping linting rule %s on file %s", rule, file_path)
                continue

            logger.debug("Running linting rule %s on file %s", rule, file_path)
            if rule in rule.warn:
                warnings.extend(rule.checkrule(str(file_path), text))

            else:
                errors.extend(rule.checkrule(str(file_path), text))

        for error in errors:
            logger.error(error.to_rich())

        for warning in warnings:
            logger.warning(warning.to_rich())

        return errors, warnings

    def __repr__(self) -> str:
        """Return a representation of a RulesCollection object.

        Returns
        -------
        str
        """
        res = []
        current_origin = None
        for rule in sorted(self.rules, key=lambda x: (x.origin, x.rule_id)):
            if rule.origin != current_origin:
                current_origin = rule.origin
                res.append(f"Origin: {rule.origin}")
            res.append(repr(rule))

        return "\n".join(res)

    def to_rich(self) -> Group:
        """Return a rich Group containing a rich Tree for each different origin for the rules.

        Each Tree contain the rule.to_rich() output

        Examples
        --------
        ```
        Origin: BUILT-IN
        ├── S0 Jinja syntax should be correct (jinja-syntax-error)
        ├── S1 <description> (single-space-decorator)
        └── V2 <description> (jinja-variable-format)
        ```
        """
        res = []
        current_origin = None
        tree = None
        for rule in sorted(self.rules, key=lambda x: (x.origin, x.rule_id)):
            if rule.origin != current_origin:
                current_origin = rule.origin
                tree = Tree(f"Origin: {rule.origin}")
                res.append(tree)
            if not tree:
                msg = "Something went wrong while converting to rich output. Please raise an issue on Github."
                raise JinjaLinterError(msg)
            tree.add(rule.to_rich())
        return Group(*res)

    def to_json(self) -> str:
        """Return a json representation of the collection as a list of the rules.

        Returns
        -------
        str
        """
        return json.dumps([json.loads(rule.to_json()) for rule in sorted(self.rules, key=lambda x: (x.origin, x.rule_id))])

    @classmethod
    def create_from_directory(cls, rules_dir: Path, ignore_rules: list[str], warn_rules: list[str]) -> RulesCollection:
        """Create a collection from all rule modules.

        Parameters
        ----------
        rules_dir
            The directory in which to look for the rules.
        ignore_rules
            List of rule short_descriptions or ids to ignore.
        warn_rules
            List of rule short_descriptions or ids to consider as warnings rather than errors.

        Returns
        -------
        RulesCollection
            A RulesColleciton object containing the rules from rules_dir except for the ignored ones.
        """
        result = cls()
        result.rules = load_plugins(rules_dir.expanduser())
        for rule in result.rules:
            if rule.short_description in ignore_rules or rule.rule_id in ignore_rules:
                rule.ignore = True
            if rule.short_description in warn_rules or rule.rule_id in warn_rules:
                rule.warn.append(rule)
        if rules_dir != DEFAULT_RULE_DIR:
            for rule in result.rules:
                rule.origin = str(rules_dir)
        logger.info("Created collection from rules directory %s", rules_dir)
        return result

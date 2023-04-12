"""collection.py - Class to create a collection of linting rules.
"""
from __future__ import annotations

import json
import os
import pathlib
from collections.abc import Iterable

from rich.console import Group
from rich.tree import Tree

from j2lint.logger import logger
from j2lint.utils import is_rule_disabled, load_plugins

from .error import LinterError
from .rule import Rule

DEFAULT_RULE_DIR = pathlib.Path(__file__).parent.parent / "rules"


class RulesCollection:
    """RulesCollection class which checks the linting rules against a file."""

    def __init__(self, verbose: bool = False) -> None:
        self.rules: list[Rule] = []
        self.verbose = verbose

    def __iter__(self) -> Iterable[Rule]:
        return iter(self.rules)

    def __len__(self) -> int:
        return len(self.rules)

    def extend(self, more: list[Rule]) -> None:
        """Extends list of rules

        Args:
            more (list): list of rules classes

        Note: This does not protect against duplicate rules
        """
        self.rules.extend(more)

    def run(
        self, file_dict: dict[str, str]
    ) -> tuple[list[LinterError], list[LinterError]]:
        """Runs the linting rules for given file

        Args:
            file_dict (dict): file path and file type

        Returns:
            tuple(list, list): a tuple containing the list of linting errors
                               and the list of linting warnings found
        """
        text = ""
        errors: list[LinterError] = []
        warnings: list[LinterError] = []

        try:
            with open(file_dict["path"], mode="r", encoding="utf-8") as file:
                text = file.read()
        except IOError as err:
            logger.warning("Could not open %s - %s", file_dict["path"], err.strerror)
            return errors, warnings

        for rule in self.rules:
            if rule.ignore:
                logger.debug(
                    "Ignoring rule %s:%s for file %s",
                    rule.rule_id,
                    rule.short_description,
                    file_dict["path"],
                )
                continue
            if is_rule_disabled(text, rule):
                logger.debug(
                    "Skipping linting rule %s on file %s", rule, file_dict["path"]
                )
                continue

            logger.debug("Running linting rule %s on file %s", rule, file_dict["path"])
            if rule in rule.warn:
                warnings.extend(rule.checkrule(file_dict, text))

            else:
                errors.extend(rule.checkrule(file_dict, text))

        for error in errors:
            logger.error(error.to_rich())

        for warning in warnings:
            logger.warning(warning.to_rich())

        return errors, warnings

    def __repr__(self) -> str:
        res = []
        current_origin = None
        for rule in sorted(self.rules, key=lambda x: (x.origin, x.rule_id)):
            if rule.origin != current_origin:
                current_origin = rule.origin
                res.append(f"Origin: {rule.origin}")
            res.append(repr(rule))

        return "\n".join(res)

    def to_rich(self) -> Group:
        """
        Return a rich Group containing a rich Tree for each different origin
        for the rules

        Each Tree contain the rule.to_rich() output

        Origin: BUILT-IN
        ├── S0 Jinja syntax should be correct (jinja-syntax-error)
        ├── S1 <description> (single-space-decorator)
        └── V2 <description> (jinja-variable-format)
        """
        res = []
        current_origin = None
        tree = None
        for rule in sorted(self.rules, key=lambda x: (x.origin, x.rule_id)):
            if rule.origin != current_origin:
                current_origin = rule.origin
                tree = Tree(f"Origin: {rule.origin}")
                res.append(tree)
            assert tree
            tree.add(rule.to_rich())
        return Group(*res)

    def to_json(self) -> str:
        """Return a json representation of the collection as a list of the rules"""
        return json.dumps(
            [
                json.loads(rule.to_json())
                for rule in sorted(self.rules, key=lambda x: (x.origin, x.rule_id))
            ]
        )

    @classmethod
    def create_from_directory(
        cls, rules_dir: str, ignore_rules: list[str], warn_rules: list[str]
    ) -> RulesCollection:
        """Creates a collection from all rule modules

        Args:
            rules_dir (string): rules directory
            ignore_rules (list): list of rule short_descriptions or ids to ignore
            warn_rules (list): list of rule short_descriptions or ids to consider as
                               warnings rather than errors

        Returns:
            list: a collection of rule objects
        """
        result = cls()
        result.rules = load_plugins(os.path.expanduser(rules_dir))
        for rule in result.rules:
            if rule.short_description in ignore_rules or rule.rule_id in ignore_rules:
                rule.ignore = True
            if rule.short_description in warn_rules or rule.rule_id in warn_rules:
                rule.warn.append(rule)
        if rules_dir != DEFAULT_RULE_DIR:
            for rule in result.rules:
                rule.origin = rules_dir
        logger.info("Created collection from rules directory %s", rules_dir)
        return result

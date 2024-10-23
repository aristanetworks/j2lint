# Copyright (c) 2021-2024 Arista Networks, Inc.
# Use of this source code is governed by the MIT license
# that can be found in the LICENSE file.
"""Pytest fixtures for j2lint testing."""

from __future__ import annotations

import logging
import pathlib
from argparse import Namespace
from pathlib import Path
from typing import Callable
from unittest.mock import MagicMock, create_autospec

import pytest

from j2lint.cli import create_parser
from j2lint.linter.collection import DEFAULT_RULE_DIR, RulesCollection
from j2lint.linter.error import LinterError
from j2lint.linter.rule import Rule
from j2lint.linter.runner import Runner

CONTENT = "content"

# Disabling redefined-outer-name as a solution for pylint
# cf https://docs.pytest.org/en/stable/reference/reference.html#pytest-fixture
# pylint: disable=fixme, redefined-outer-name

# TODO: proper way to compare LinterError following:
# https://docs.pytest.org/en/7.1.x/how-to/assert.html#defining-your-own-explanation-for-failed-assertions


class TestRule(Rule):
    """TestRule class for tests."""

    rule_id = "TT"
    description = "test"
    short_description = "test"
    severity = "LOW"

    def checktext(self, filename: Path, text: str) -> list[LinterError]:
        """Fake checktext implementation."""
        return []

    def checkline(self, filename: Path, line: int, line_no: int) -> list[LinterError]:
        """Fake checkline implementation."""
        return []


@pytest.fixture
def collection() -> RulesCollection:
    """Return the collection with the default rules."""
    return RulesCollection.create_from_directory(DEFAULT_RULE_DIR, [], [])


@pytest.fixture
def make_rules() -> Callable[[int], list[Rule]]:
    """Return a Rule factory that takes one argument `count` and returns count rules.

    The rules arefollowing the pattern where `i` is the index

    ```
    rule_id = Ti
    description = test rule i
    short_description = test-rule-i
    severity in [LOW, MEDIUM, HIGH] based on i % 3
    ```

    Examples
    --------
    The factory can then be invoked as follow:

    ```
    def test_blah(makes_rules):
        rules = make_rules(5)
        # do stuff with rules
    ```
    """

    def __make_n_rules(count: int) -> list[Rule]:
        def get_severity(integer: int) -> str:
            """Return a severity based on the integer modulo 3."""
            return "LOW" if integer % 3 == 0 else ("MEDIUM" if integer % 3 == 1 else "HIGH")

        rules = []
        for i in range(count):
            r_obj = TestRule()
            r_obj.rule_id = f"T{i}"
            r_obj.description = f"test rule {i}"
            r_obj.short_description = f"test-rule-{i}"
            r_obj.severity = get_severity(i)
            rules.append(r_obj)
        return rules

    return __make_n_rules


@pytest.fixture
def test_rule(make_rules: Callable[[int], list[Rule]]) -> Rule:
    """Return a Rule object to use in test from the make_rules fixture.

    The rule is

    ```
    rule_id = T0
    description = test rule 0
    short_description = test-rule-0
    severity = LOW
    ```
    """
    return make_rules(1)[0]


@pytest.fixture
def test_other_rule(make_rules: Callable[[int], list[Rule]]) -> Rule:
    """Return the second  Rule object to use in test from the make_rules fixture.

    The rule is:

    ```
    rule_id = T1
    description = test rule 1
    short_description = test-rule-1
    severity = MEDIUM
    ```
    """
    return make_rules(2)[1]


@pytest.fixture
def make_issues(make_rules: Callable[[int], list[Rule]]) -> Callable[[int], list[LinterError]]:
    """Return a factory that generates `count` issues and return them as a list.

    The fixture invokes `make_rules` first with count
    and every LinterError generated is using the rule
    of same index.

    The line number is index + 1 so issue 0 will have
    line number 1

    the line content is always "dummy" and the filename
    "dummy.j2"

    The factory can then be invoked as follow:

    ```
    def test_blah(makes_issues):
        issues = make_issues(5)
        # do stuff with issues
    ```
    """

    def __make_n_issues(count: int) -> list[LinterError]:
        rules = make_rules(count)
        return [LinterError(i + 1, "dummy", "dummy.j2", rules[i]) for i in range(count)]

    return __make_n_issues


@pytest.fixture
def make_issue_from_rule() -> Callable[[Rule], LinterError]:
    """Return a factory that generates an issue based on a Rule object.

    it uses line 42, the line content is "dummy" and the filename is "dummy.j2".
    """

    def __make_issue_from_rule(rule: Rule) -> LinterError:
        yield LinterError(42, "dummy", "dummy.j2", rule)

    return __make_issue_from_rule


@pytest.fixture
def test_issue(make_issues: Callable[[int], list[Rule]]) -> LinterError:
    """Get the first issue from the make_issues factory.

    It will use rule T0 as per design.
    """
    return make_issues(1)[0]


@pytest.fixture
def test_collection(test_rule: Rule) -> RulesCollection:
    """test_collection using one rule `test_rule`."""
    collection = RulesCollection()
    collection.extend([test_rule])
    return collection


@pytest.fixture
def test_runner(test_collection: RulesCollection) -> Runner:
    """Fixture to get a test runner using the test_collection."""
    return Runner(test_collection, "test.j2", checked_files=[])


@pytest.fixture
def j2lint_usage_string() -> str:
    """Fixture to get the help generated by argparse."""
    return create_parser().format_help()


@pytest.fixture
def template_tmp_dir(tmp_path_factory: object) -> list[str]:
    """Create a tmp directory with multiple files and hidden files."""
    tmp_dir = pathlib.Path(__file__).parent / "tmp"

    # https://stackoverflow.com/questions/40566968/how-to-dynamically-change-pytests-tmpdir-base-directory
    # +
    # https://docs.pytest.org/en/7.1.x/_modules/_pytest/tmpdir.html
    # Using _given_basetemp to trigger creation
    # pylint: disable=protected-access
    tmp_path_factory._given_basetemp = tmp_dir

    rules = tmp_path_factory.mktemp("rules", numbered=False)

    rules_subdir = rules / "rules_subdir"
    rules_subdir.mkdir()
    # no clue if we are suppose to find these
    rules_hidden_subdir = rules / ".rules_hidden_subdir"
    rules_hidden_subdir.mkdir()

    # in each directory add one matching file and one none matching
    rules_j2 = rules / "rules.j2"
    rules_j2.write_text(CONTENT)
    rules_txt = rules / "rules.txt"
    rules_txt.write_text(CONTENT)

    rules_subdir_j2 = rules_subdir / "rules.j2"
    rules_subdir_j2.write_text(CONTENT)
    rules_subdir_txt = rules_subdir / "rules.txt"
    rules_subdir_txt.write_text(CONTENT)

    rules_hidden_subdir_j2 = rules_hidden_subdir / "rules.j2"
    rules_hidden_subdir_j2.write_text(CONTENT)
    rules_hidden_subdir_txt = rules_hidden_subdir / "rules.txt"
    rules_hidden_subdir_txt.write_text(CONTENT)

    return [str(rules)]


@pytest.fixture
def default_namespace() -> Namespace:
    """Return the default ArgParse namespace for j2lint."""
    return Namespace(
        files=[],
        ignore=[],
        warn=[],
        list=False,
        rules_dir=[DEFAULT_RULE_DIR],
        verbose=False,
        debug=False,
        json=False,
        stdin=False,
        log=False,
        version=False,
        stdout=False,
    )


@pytest.fixture
def logger() -> MagicMock:
    """Return a MagicMock object with the spec of logging.Logger."""
    return create_autospec(logging.Logger)

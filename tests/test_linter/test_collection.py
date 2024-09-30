# Copyright (c) 2021-2024 Arista Networks, Inc.
# Use of this source code is governed by the MIT license
# that can be found in the LICENSE file.
"""Tests for j2lint.linter.collection.py."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING, Callable
from unittest import mock

import pytest

from j2lint.linter.collection import RulesCollection
from j2lint.rules.jinja_operator_has_spaces_rule import JinjaOperatorHasSpacesRule
from j2lint.rules.jinja_statement_delimiter_rule import JinjaStatementDelimiterRule
from j2lint.rules.jinja_template_syntax_error_rule import JinjaTemplateSyntaxErrorRule

if TYPE_CHECKING:
    from j2lint.linter.error import LinterError
    from j2lint.linter.rule import Rule

TEST_DATA_DIR = Path(__file__).parent / "data"


class TestRulesCollection:
    """Test j2lint.linter.collection.RulesCollection."""

    def test__len__(self, test_collection: RulesCollection) -> None:
        """Test the RuleCollection __len__ method."""
        assert len(test_collection) == 1

    def test__iter__(self) -> None:
        """Test the RuleCollection __iter__ method."""
        fake_rules = [1, 2, 3]
        collection = RulesCollection()
        assert len(collection) == 0
        collection.rules = fake_rules
        for index, rule in enumerate(collection):
            assert rule == fake_rules[index]

    def test_extend(self) -> None:
        """Test the RuleCollection.extend method."""
        fake_rules = [1, 2, 3]
        collection = RulesCollection()
        assert len(collection) == 0
        collection.rules.extend(fake_rules)
        assert len(collection) == len(fake_rules)
        collection.rules.extend(fake_rules)
        assert len(collection) == 2 * len(fake_rules)
        assert collection.rules == fake_rules + fake_rules

    @pytest.mark.parametrize(
        ("file_path", "expected_results", "verify_logs"),
        [
            pytest.param(
                "dummy.j2",
                ([], []),
                False,
                id="non existing file",
            ),
            pytest.param(
                f"{TEST_DATA_DIR}/disable-rule-3.j2",
                (
                    [
                        ("T0", "test-rule-0"),
                        ("T4", "test-rule-4"),
                    ],
                    [
                        ("T1", "test-rule-1"),
                    ],
                ),
                True,
                id="Disabled Rule 3",
            ),
        ],
    )
    def test_run(
        self,
        caplog: pytest.LogCaptureFixture,
        test_collection: RulesCollection,
        make_rules: Callable[[int], list[Rule]],
        make_issue_from_rule: Callable[[int], LinterError],
        file_path: Path,
        expected_results: tuple[list[tuple[str, str]], list[tuple[str, str]]],
        *,
        verify_logs: bool,
    ) -> None:
        """Test RulesCollection.run on a generated collection.

        The collection has 5 rules with.
         * rule number 1 being a warning
         * rule number 2 being ignored
         * rule number 3 being disabled in the test file for test number 2

        """
        caplog.set_level(logging.DEBUG)
        rules = make_rules(5)
        # make rule number 1 be a warning
        rules[1].warn.append(rules[1])
        rules[2].ignore = True
        test_collection.rules = rules

        def checks_side_effect(self, file_path: Path, text: str) -> None:  # type: ignore[no-untyped-def] # noqa: ARG001, ANN001
            return make_issue_from_rule(self)

        with mock.patch(
            "j2lint.linter.rule.Rule.checkrule",
            side_effect=checks_side_effect,
            autospec=True,
        ):
            errors, warnings = test_collection.run(Path(file_path))
            error_tuples = [(error.rule.rule_id, error.rule.short_description) for error in errors]
            warning_tuples = [(warning.rule.rule_id, warning.rule.short_description) for warning in warnings]
            assert error_tuples == expected_results[0]
            assert warning_tuples == expected_results[1]

        if verify_logs:
            # True for every test that goes beyond the file do not exist
            assert any("Ignoring rule T2" in message for message in caplog.messages)
            # True for the test file
            assert any("Skipping linting rule T3" in message for message in caplog.messages)

    def test__repr__(self, test_collection: RulesCollection, test_other_rule: Rule) -> None:
        """Test the RuleCollection.extend method."""
        assert str(test_collection) == "Origin: BUILT-IN\nT0: test rule 0"
        test_other_rule.origin = "DUMMY"
        test_collection.extend([test_other_rule])
        assert str(test_collection) == "Origin: BUILT-IN\nT0: test rule 0\nOrigin: DUMMY\nT1: test rule 1"

    @pytest.mark.parametrize(
        ("ignore_rules", "warn_rules"),
        [
            pytest.param(["S0", "operator-enclosed-by-spaces"], [], id="no_warn_no_ignore"),
            pytest.param([], ["S0", "operator-enclosed-by-spaces"], id="warn_no_ignore"),
            pytest.param(["S0"], ["operator-enclosed-by-spaces"], id="ignore_no_warn"),
            pytest.param([], ["S42"], id="ignore_absent_rule"),
            pytest.param(["S42"], [], id="warn_absent_rule"),
        ],
    )
    def test_create_from_directory(self, ignore_rules: list[str], warn_rules: list[str]) -> None:
        """Test the RuleCollection.create_from_directory class method.

        In this tests, the return of load_plugins are mocked.
        consequently, a dummy path can be used for rules_dir
        """
        with mock.patch("j2lint.linter.collection.load_plugins") as mocked_load_plugins:
            # importing 3 rules for the need of the tests
            # note that current pylint branch is returning classes
            # not instances..
            mocked_load_plugins.return_value = [
                JinjaStatementDelimiterRule(),
                JinjaOperatorHasSpacesRule(),
                JinjaTemplateSyntaxErrorRule(),
            ]
            collection = RulesCollection.create_from_directory(Path("dummy"), ignore_rules, warn_rules)
            mocked_load_plugins.assert_called_once_with("dummy")
            assert collection.rules == mocked_load_plugins.return_value
            for rule in collection.rules:
                if rule.rule_id in ignore_rules or rule.short_description in ignore_rules:
                    assert rule.ignore is True
                if rule.rule_id in warn_rules or rule.short_description in warn_rules:
                    assert rule in rule.warn

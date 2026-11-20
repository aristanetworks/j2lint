# Copyright (c) 2021-2026 Arista Networks, Inc.
# Use of this source code is governed by the MIT license
# that can be found in the LICENSE file.
"""Tests for j2lint.linter.collection.py."""

from __future__ import annotations

import json
import logging
import os
import subprocess
import sys
from pathlib import Path
from textwrap import dedent
from types import MethodType
from typing import TYPE_CHECKING, Any, assert_type
from unittest import mock

import pytest

from j2lint.linter.collection import RulesCollection
from j2lint.linter.rule import Rule
from j2lint.rules.jinja_operator_has_spaces_rule import JinjaOperatorHasSpacesRule
from j2lint.rules.jinja_statement_delimiter_rule import JinjaStatementDelimiterRule
from j2lint.rules.jinja_template_no_tabs_rule import JinjaTemplateNoTabsRule
from j2lint.rules.jinja_template_syntax_error_rule import JinjaTemplateSyntaxErrorRule
from j2lint.utils import mask_raw_block_contents

if TYPE_CHECKING:
    from collections.abc import Callable

    from j2lint.linter.error import LinterError

TEST_DATA_DIR = Path(__file__).parent / "data"


class TestRulesCollection:
    """Test j2lint.linter.collection.RulesCollection."""

    def test__len__(self, test_collection: RulesCollection) -> None:
        """Test the RuleCollection __len__ method."""
        assert len(test_collection) == 1

    def test_create_from_directory_subclass(self) -> None:
        """The inherited factory preserves the subclass at runtime and in its return type."""

        class CustomCollection(RulesCollection):
            """A collection subclass used to check the factory return type."""

        with mock.patch("j2lint.linter.collection.load_plugins", return_value=[]):
            collection = CustomCollection.create_from_directory(Path("dummy"), [], [])

        assert_type(collection, CustomCollection)
        assert isinstance(collection, CustomCollection)

    def test__iter__(self, make_rules: Callable[[int], list[Rule]]) -> None:
        """Test the RuleCollection __iter__ method."""
        fake_rules = make_rules(3)
        collection = RulesCollection()
        assert len(collection) == 0
        collection.rules = fake_rules
        for index, rule in enumerate(collection):
            assert rule == fake_rules[index]

    def test_extend(self, make_rules: Callable[[int], list[Rule]]) -> None:
        """Test the RuleCollection.extend method."""
        fake_rules = make_rules(3)
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
        make_issue_from_rule: Callable[[Rule], LinterError],
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

        def checks_side_effect(self: Rule, _file_path: Path, _text: str) -> list[LinterError]:
            return [make_issue_from_rule(self)]

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

    def test_run_shares_preparation_and_preserves_diagnostics(self, tmp_path: Path) -> None:
        """Share masking across error and warning rules without masking reported source."""
        path = tmp_path / "template.j2"
        text = "{% raw %}\t{% endraw %}\t\n# \tignored\n\tvisible\n"
        path.write_text(text, encoding="utf-8")
        error_rule = JinjaTemplateNoTabsRule()
        warning_rule = JinjaTemplateNoTabsRule()
        warning_rule.warn.append(warning_rule)
        collection = RulesCollection()
        collection.extend([error_rule, warning_rule])

        with mock.patch("j2lint.linter.rule.mask_raw_block_contents", wraps=mask_raw_block_contents) as mask:
            errors, warnings = collection.run(path)

        mask.assert_called_once_with(text)
        expected = [(1, text.split("\n", maxsplit=1)[0]), (3, "\tvisible")]
        assert [(error.line_number, error.line) for error in errors] == expected
        assert [(warning.line_number, warning.line) for warning in warnings] == expected
        assert all(error.filename == str(path) and error.rule is error_rule for error in errors)
        assert all(warning.rule is warning_rule for warning in warnings)

    def test_run_prepares_each_file_invocation_independently(self, tmp_path: Path) -> None:
        """Reusing a collection and filename must not reuse stale prepared lines."""
        path = tmp_path / "template.j2"
        collection = RulesCollection()
        collection.extend([JinjaTemplateNoTabsRule(), JinjaTemplateNoTabsRule()])

        with mock.patch("j2lint.linter.rule.mask_raw_block_contents", wraps=mask_raw_block_contents) as mask:
            path.write_text("{% raw %}\t{% endraw %}\n", encoding="utf-8")
            assert collection.run(path) == ([], [])
            path.write_text("\tvisible\n", encoding="utf-8")
            errors, warnings = collection.run(path)
            other_path = tmp_path / "other.j2"
            other_path.write_text("plain text", encoding="utf-8")
            assert collection.run(other_path) == ([], [])

        assert mask.call_count == 3
        assert [(error.line_number, error.line) for error in errors] == [(1, "\tvisible"), (1, "\tvisible")]
        assert not warnings

    @pytest.mark.parametrize("mode", ["text-only", "ignored", "disabled", "empty", "unreadable"])
    def test_run_does_not_prepare_unused_lines(self, tmp_path: Path, mode: str) -> None:
        """Only an active line-based rule should trigger preparation."""
        path = tmp_path / "template.j2"
        path.write_text("{# j2lint: disable=S5 #}\nplain text\n", encoding="utf-8")
        collection = RulesCollection()
        if mode == "text-only":
            collection.extend([JinjaTemplateSyntaxErrorRule()])
        elif mode != "empty":
            collection.extend([JinjaTemplateNoTabsRule()])
            collection.rules[0].ignore = mode == "ignored"
        if mode == "unreadable":
            path = tmp_path / "missing.j2"

        with mock.patch("j2lint.linter.rule.mask_raw_block_contents", side_effect=AssertionError("unexpected masking")):
            assert collection.run(path) == ([], [])

    def test_run_honors_custom_checkrule_override(self, tmp_path: Path) -> None:
        """A custom override can still delegate to the public base implementation."""
        calls: list[tuple[str, str]] = []

        # Inherited checktext intentionally raises NotImplementedError to select the checkline fallback.
        class CustomRule(JinjaTemplateNoTabsRule):  # pylint: disable=abstract-method
            """Record public dispatch before performing normal checks."""

            def checkrule(self, filename: str, text: str) -> list[LinterError]:
                calls.append((filename, text))
                return super().checkrule(filename, text)

        path = tmp_path / "template.j2"
        text = "\tvisible"
        path.write_text(text, encoding="utf-8")
        rule = CustomRule()
        collection = RulesCollection()
        collection.extend([rule])
        errors, warnings = collection.run(path)

        assert calls == [(str(path), text)]
        assert [(error.line_number, error.line) for error in errors] == [(1, text)]
        assert not warnings

    def test_run_honors_instance_checkrule_override(self, tmp_path: Path) -> None:
        """Instance-level replacements must not be bypassed by shared preparation."""
        path = tmp_path / "template.j2"
        path.write_text("\tvisible", encoding="utf-8")
        rule = JinjaTemplateNoTabsRule()
        collection = RulesCollection()
        collection.extend([rule])

        with mock.patch.object(rule, "checkrule", wraps=rule.checkrule) as checkrule:
            errors, _ = collection.run(path)

        checkrule.assert_called_once_with(str(path), "\tvisible")
        assert len(errors) == 1

    @pytest.mark.parametrize("forward_class", [False, True], ids=["method-attributes", "transparent-class"])
    def test_run_honors_callable_checkrule_proxy(self, tmp_path: Path, *, forward_class: bool) -> None:
        """Callable proxies must retain their behavior even when they expose method metadata."""
        forwarded = {"__func__", "__self__", "__name__"}
        if forward_class:
            forwarded.add("__class__")

        class CheckruleProxy:  # pylint: disable=too-few-public-methods
            """Wrap a bound method while suppressing diagnostics and recording calls."""

            def __init__(self, wrapped: Callable[[str, str], list[LinterError]]) -> None:
                self.wrapped = wrapped
                self.calls: list[tuple[str, str]] = []

            def __getattribute__(self, name: str) -> Any:
                if name in forwarded:
                    return getattr(object.__getattribute__(self, "wrapped"), name)
                return object.__getattribute__(self, name)

            def __call__(self, filename: str, text: str) -> list[LinterError]:
                self.calls.append((filename, text))
                return []

        path = tmp_path / "template.j2"
        text = "\tvisible"
        path.write_text(text, encoding="utf-8")
        rule = JinjaTemplateNoTabsRule()
        proxy = CheckruleProxy(rule.checkrule)
        # A transparent proxy can even make isinstance look like a native method.
        assert isinstance(proxy, MethodType) is forward_class
        collection = RulesCollection()
        collection.extend([rule])

        with mock.patch.object(rule, "checkrule", new=proxy):
            assert not rule.checkrule(str(path), text)
            errors, warnings = collection.run(path)

        assert proxy.calls == [(str(path), text), (str(path), text)]
        assert not errors
        assert not warnings

    @pytest.mark.parametrize(
        ("receiver_type", "delegate_type", "text", "expected_rule_id"),
        [
            (JinjaTemplateNoTabsRule, JinjaTemplateSyntaxErrorRule, "{{ broken", "S0"),
            (JinjaTemplateSyntaxErrorRule, JinjaTemplateNoTabsRule, "\tvisible", "S5"),
        ],
    )
    def test_run_honors_checkrule_bound_to_another_rule(
        self, tmp_path: Path, receiver_type: type[Rule], delegate_type: type[Rule], text: str, expected_rule_id: str
    ) -> None:
        """Rebinding an inherited method must preserve its receiver and diagnostics."""
        path = tmp_path / "template.j2"
        path.write_text(text, encoding="utf-8")
        receiver = receiver_type()
        delegate = delegate_type()
        expected_errors = delegate.checkrule(str(path), text)
        collection = RulesCollection()
        collection.extend([receiver])

        with mock.patch.object(receiver, "checkrule", new=delegate.checkrule):
            errors, warnings = collection.run(path)

        assert [error.rule.rule_id for error in errors] == [expected_rule_id]
        assert all(error.rule is delegate for error in errors)
        assert [error.to_json() for error in errors] == [error.to_json() for error in expected_errors]
        assert not warnings

    def test_run_honors_base_checkrule_replacement(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Replacing the base implementation should still intercept public dispatch."""
        path = tmp_path / "template.j2"
        path.write_text("\tvisible", encoding="utf-8")
        calls: list[str] = []
        original_checkrule = Rule.checkrule

        def checkrule(rule: Rule, filename: str, text: str) -> list[LinterError]:
            calls.append(filename)
            return original_checkrule(rule, filename, text)

        monkeypatch.setattr(Rule, "checkrule", checkrule)
        collection = RulesCollection()
        collection.extend([JinjaTemplateNoTabsRule()])
        errors, _ = collection.run(path)

        assert calls == [str(path)]
        assert len(errors) == 1

    def test_run_honors_base_checkrule_replacement_before_collection_import(self, tmp_path: Path) -> None:
        """Startup replacements must be honored regardless of collection import order."""
        path = tmp_path / "template.j2"
        text = "\tvisible"
        path.write_text(text, encoding="utf-8")
        script = dedent("""\
            import json
            import sys
            from pathlib import Path

            from j2lint.linter.rule import Rule

            collection_loaded_before_patch = "j2lint.linter.collection" in sys.modules
            calls = []

            def replacement(self, filename, text):
                calls.append([filename, text])
                return []

            Rule.checkrule = replacement

            from j2lint.linter.collection import RulesCollection
            from j2lint.rules.jinja_template_no_tabs_rule import JinjaTemplateNoTabsRule

            collection = RulesCollection()
            collection.extend([JinjaTemplateNoTabsRule()])
            errors, warnings = collection.run(Path(sys.argv[1]))
            print(json.dumps({
                "collection_loaded_before_patch": collection_loaded_before_patch,
                "calls": calls,
                "errors": [json.loads(error.to_json()) for error in errors],
                "warnings": [json.loads(warning.to_json()) for warning in warnings],
            }))
            """)
        env = dict(os.environ, PYTHONPATH=str(Path(__file__).resolve().parents[2]))
        completed = subprocess.run(  # noqa: S603 - controlled interpreter and regression script
            [sys.executable, "-c", script, str(path)], capture_output=True, text=True, check=True, timeout=30, cwd=tmp_path, env=env
        )

        assert json.loads(completed.stdout) == {
            "collection_loaded_before_patch": False,
            "calls": [[str(path), text]],
            "errors": [],
            "warnings": [],
        }
        assert not completed.stderr

    def test_run_does_not_reuse_preparation_after_rule_failure(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """A failed invocation must not leave stale prepared data on the collection."""
        path = tmp_path / "template.j2"
        path.write_text("\tfirst", encoding="utf-8")
        rule = JinjaTemplateNoTabsRule()
        collection = RulesCollection()
        collection.extend([rule])
        with monkeypatch.context() as patch:
            patch.setattr(rule, "checkline", mock.Mock(side_effect=RuntimeError("custom check failed")))
            with pytest.raises(RuntimeError, match="custom check failed"):
                collection.run(path)

        path.write_text("plain text", encoding="utf-8")
        assert collection.run(path) == ([], [])

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
            # not instances.
            mocked_load_plugins.return_value = [
                JinjaStatementDelimiterRule(),
                JinjaOperatorHasSpacesRule(),
                JinjaTemplateSyntaxErrorRule(),
            ]
            collection = RulesCollection.create_from_directory(Path("dummy"), ignore_rules, warn_rules)
            mocked_load_plugins.assert_called_once_with(Path("dummy"))
            assert collection.rules == mocked_load_plugins.return_value
            assert isinstance(collection, RulesCollection)
            # Somehow pylint is convinced that rule are integers
            #  pylint: disable=no-member
            for rule in collection.rules:
                if rule.rule_id in ignore_rules or rule.short_description in ignore_rules:
                    assert rule.ignore is True
                if rule.rule_id in warn_rules or rule.short_description in warn_rules:
                    assert rule in rule.warn

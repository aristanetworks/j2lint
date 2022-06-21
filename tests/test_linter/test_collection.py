"""
Tests for j2lint.linter.collection.py
"""
import logging
import pytest
from unittest import mock

from j2lint.linter.collection import RulesCollection
from j2lint.rules.JinjaTemplateSyntaxErrorRule import JinjaTemplateSyntaxErrorRule
from j2lint.rules.JinjaOperatorHasSpaceRule import JinjaOperatorHasSpaceRule
from j2lint.rules.JinjaStatementDelimiterRule import JinjaStatementDelimiterRule

from tests.utils import does_not_raise


class TestRulesCollection:
    def test__len__(self, test_collection):
        """
        Test the RuleCollection __len__ method
        """
        assert len(test_collection) == 1

    def test__iter__(self):
        """
        Test the RuleCollection __iter__ method
        """
        fake_rules = [1, 2, 3]
        collection = RulesCollection()
        assert len(collection) == 0
        collection.rules = fake_rules
        for index, rule in enumerate(collection):
            assert rule == fake_rules[index]

    def test_extend(self):
        """
        Test the RuleCollection.extend method
        """
        fake_rules = [1, 2, 3]
        collection = RulesCollection()
        assert len(collection) == 0
        collection.rules.extend(fake_rules)
        assert len(collection) == len(fake_rules)
        collection.rules.extend(fake_rules)
        assert len(collection) == 2 * len(fake_rules)
        assert collection.rules == fake_rules + fake_rules

    @pytest.mark.parametrize(
        "file_dict, expected_results, verify_logs",
        [
            pytest.param(
                {"path": "dummy.j2"},
                ([], []),
                False,
                id="non existing file",
            ),
            pytest.param(
                {"path": "tests/test_linter/data/disable-rule-3.j2"},
                (
                    [
                        ("T0", "test-rule-0"),
                        ("T0", "test-rule-0"),
                        ("T4", "test-rule-4"),
                        ("T4", "test-rule-4"),
                    ],
                    [
                        ("T1", "test-rule-1"),
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
        caplog,
        test_collection,
        make_rules,
        make_issue_from_rule,
        file_dict,
        expected_results,
        verify_logs,
    ):
        """
        Generate a collection with 5 rules with:
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

        def checks_side_effect(self, file_dict, text):
            return make_issue_from_rule(self)

        with mock.patch(
            "j2lint.linter.rule.Rule.checklines",
            side_effect=checks_side_effect,
            autospec=True,
        ) as patched_checklines, mock.patch(
            "j2lint.linter.rule.Rule.checkfulltext",
            side_effect=checks_side_effect,
            autospec=True,
        ) as patched_checkfulltext:

            errors, warnings = test_collection.run(file_dict)
            error_tuples = [
                (error.rule.id, error.rule.short_description) for error in errors
            ]
            warning_tuples = [
                (warning.rule.id, warning.rule.short_description)
                for warning in warnings
            ]
            assert error_tuples == expected_results[0]
            assert warning_tuples == expected_results[1]

        if verify_logs:
            # True for every test that goes beyond the file do not exist
            assert any("Ignoring rule T2" in message for message in caplog.messages)
            # True for the test file
            assert any(
                "Skipping linting rule T3" in message for message in caplog.messages
            )

    def test__repr__(self, test_collection, test_other_rule):
        """
        Test the RuleCollection.extend method
        """
        assert str(test_collection) == "T0: test Rule object"
        test_collection.extend([test_other_rule])
        assert (
            str(test_collection) == "T0: test Rule object\nT1: other test Rule object"
        )

    # FIXME
    # when removing the support for deprecating-short-description
    # remove the appropriate test
    @pytest.mark.parametrize(
        "ignore_rules, warn_rules",
        [
            pytest.param(
                ["S0", "operator-enclosed-by-spaces"], [], id="no_warn_no_ignore"
            ),
            pytest.param(
                [], ["S0", "operator-enclosed-by-spaces"], id="warn_no_ignore"
            ),
            pytest.param(["S0"], ["operator-enclosed-by-spaces"], id="ignore_no_warn"),
            pytest.param([], ["S42"], id="ignore_absent_rule"),
            pytest.param(["S42"], [], id="warn_absent_rule"),
            pytest.param(
                ["jinja-statements-delimeter"],
                [],
                id="deprecated_short_description",
            ),
        ],
    )
    def test_create_from_directory(self, ignore_rules, warn_rules):
        """
        Test the RuleCollection.create_from_directory class method

        In this tests, the return of load_plugins are mocked.
        consequently, a dummy path can be used for rules_dir
        """
        with mock.patch("j2lint.linter.collection.load_plugins") as mocked_load_plugins:
            # importing 3 rules for the need of the tests
            # note that current pylint branch is returning classes
            # not instances..
            mocked_load_plugins.return_value = [
                JinjaStatementDelimiterRule(),
                JinjaOperatorHasSpaceRule(),
                JinjaTemplateSyntaxErrorRule(),
            ]
            collection = RulesCollection.create_from_directory(
                "dummy", ignore_rules, warn_rules
            )
            mocked_load_plugins.assert_called_once_with("dummy")
            assert collection.rules == mocked_load_plugins.return_value
            for rule in collection.rules:
                if rule.id in ignore_rules or rule.short_description in ignore_rules:
                    assert rule.ignore is True
                elif (
                    hasattr(rule, "deprecated_short_description")
                    and rule.deprecated_short_description in ignore_rules
                ):
                    assert rule.ignore is True
                if rule.id in warn_rules or rule.short_description in warn_rules:
                    assert rule in rule.warn
                elif (
                    hasattr(rule, "deprecated_short_description")
                    and rule.deprecated_short_description in warn_rules
                ):
                    assert rule in rule.warn

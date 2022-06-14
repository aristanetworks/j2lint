"""
Tests for j2lint.linter.collection.py
"""
import pytest
from unittest import mock

from j2lint.linter.collection import RulesCollection
from j2lint.rules.JinjaTemplateSyntaxErrorRule import JinjaTemplateSyntaxErrorRule
from j2lint.rules.JinjaOperatorHasSpaceRule import JinjaOperatorHasSpaceRule
from j2lint.rules.JinjaStatementDelimiterRule import JinjaStatementDelimiterRule


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

    @pytest.mark.skip("TODO")
    def test_run(self):
        """ """

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

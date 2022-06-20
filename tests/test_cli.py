"""
Tests for j2lint.cli.py
"""
from unittest.mock import create_autospec
from argparse import Namespace

import pytest

from j2lint.settings import settings
from j2lint.cli import sort_issues, sort_and_print_issues
from j2lint.linter.error import LinterError


@pytest.mark.parametrize(
    "number_issues, modifications, expected_sorted_issues_ids",
    [
        (0, {}, []),
        (1, {}, [("dummy.j2", "T0", 1, "test-rule-0")]),
        (
            2,
            {},
            [
                ("dummy.j2", "T0", 1, "test-rule-0"),
                ("dummy.j2", "T1", 2, "test-rule-1"),
            ],
        ),
        pytest.param(
            2,
            {2: {"filename": "aaa.j2"}},
            [("aaa.j2", "T1", 2, "test-rule-1"), ("dummy.j2", "T0", 1, "test-rule-0")],
            id="filename",
        ),
        pytest.param(
            2,
            {2: {"rule": {"id": "AA"}, "linenumber": 1}},
            [
                ("dummy.j2", "AA", 1, "test-rule-1"),
                ("dummy.j2", "T0", 1, "test-rule-0"),
            ],
            id="rule id",
        ),
    ],
)
def test_sort_issues(
    make_issues, number_issues, modifications, expected_sorted_issues_ids
):
    """
    Test j2lint.cli.sort_issues
    """
    issues = make_issues(number_issues, "DUMMY")
    # In the next step we apply modifications on the generated LinterErrors
    # if required
    for index, modification in modifications.items():
        for key, value in modification.items():
            if isinstance(value, dict):
                nested_obj = getattr(issues["DUMMY"][index - 1], key)
                for n_key, n_value in value.items():
                    setattr(nested_obj, n_key, n_value)
            else:
                setattr(issues["DUMMY"][index - 1], key, value)
    sorted_issues = sort_issues(issues["DUMMY"])
    sorted_issues_ids = [
        (issue.filename, issue.rule.id, issue.linenumber, issue.rule.short_description)
        for issue in sorted_issues
    ]
    assert sorted_issues_ids == expected_sorted_issues_ids


@pytest.mark.parametrize(
    "options, number_issues, issue_type, expected_output, expected_stdout",
    [
        pytest.param(
            Namespace(json=False), 0, "ERRORS", (0, {}), "", id="No issue - cli"
        ),
        pytest.param(
            Namespace(json=True), 0, "ERRORS", (0, {}), "", id="No issue - json"
        ),
        pytest.param(
            Namespace(json=False),
            1,
            "ERRORS",
            (1, {}),
            "\nJINJA2 LINT ERRORS\n************ File ERRORS\ndummy.j2:1 test rule 0 (test-rule-0)\n",
            id="One issue - cli",
        ),
        pytest.param(
            Namespace(json=True),
            1,
            "ERRORS",
            (
                1,
                {
                    "ERRORS": [
                        {
                            "filename": "dummy.j2",
                            "id": "T0",
                            "line": "dummy",
                            "linenumber": 1,
                            "message": "test rule 0",
                            "severity": "LOW",
                        }
                    ]
                },
            ),
            "",
            id="One issue - json",
        ),
    ],
)
def test_sort_and_print_issues(
    capsys,
    make_issues,
    options,
    number_issues,
    issue_type,
    expected_output,
    expected_stdout,
):
    """
    Test j2lint.cli.sort_and_print_issues

    The method is a bit of a mess to test as it relies heavily on the
    inputs being passed being correct (for instance if you pass the lint_warnings
    with an issue_type of ERROR, it will just print all teh warnings under error).

    This test hence just aims at verifying that the method prints correctly without
    any further checks.
    """
    # we need to make sure settings is correct to print the issues as JSON
    # TODO - this is bad practice to expect __repr__ to select the output
    # from settings.. to be fixed later..
    #
    # this is not reset between tests so need to reset it..
    if options.json:
        settings.output = "json"

    issues = make_issues(number_issues, issue_type)
    json_output = {}
    total_count, json_output = sort_and_print_issues(
        options, issues, issue_type, json_output
    )

    try:
        assert total_count == expected_output[0]
        assert json_output == expected_output[1]

        captured = capsys.readouterr()
        assert captured.out == expected_stdout
    finally:
        # Reverting back to default
        settings.output = "text"

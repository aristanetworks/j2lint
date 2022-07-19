"""
Tests for j2lint.linter.error.py
"""
import pytest

RULE_TEXT_OUTPUT = (
    "Linting rule: T0\n"
    "Rule description: test rule 0\n"
    "Error line: dummy.j2:1 dummy\n"
    "Error message: test rule 0\n"
)
RULE_JSON_OUTPUT = (
    '{"id": "T0", "message": "test rule 0", '
    '"filename": "dummy.j2", "line_number": 1, '
    '"line": "dummy", "severity": "LOW"}'
)


@pytest.mark.parametrize(
    "verbose, expected",
    [
        (False, "dummy.j2:1 test rule 0 (test-rule-0)"),
        (
            True,
            RULE_TEXT_OUTPUT,
        ),
    ],
)
def test_to_string(test_issue, verbose, expected):
    """
    Test the string formats for LinterError
    """

    assert test_issue.to_string(verbose) == expected


def test_to_json(test_issue):
    """
    Test the json format for LinterError
    """

    assert test_issue.to_json() == RULE_JSON_OUTPUT

# Copyright (c) 2023 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the LICENSE file.
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
def test_to_rich(test_issue, verbose, expected):
    """
    Test the Rich string formats for LinterError
    """

    assert str(test_issue.to_rich(verbose)) == expected


def test_to_json(test_issue):
    """
    Test the json format for LinterError
    """

    assert test_issue.to_json() == RULE_JSON_OUTPUT

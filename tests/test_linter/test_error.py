# Copyright (c) 2021-2024 Arista Networks, Inc.
# Use of this source code is governed by the MIT license
# that can be found in the LICENSE file.
"""Tests for j2lint.linter.error.py."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from j2lint.linter.error import LinterError

RULE_TEXT_OUTPUT = "Linting rule: T0\nRule description: test rule 0\nError line: dummy.j2:1 dummy\nError message: test rule 0\n"
RULE_JSON_OUTPUT = '{"id": "T0", "message": "test rule 0", "filename": "dummy.j2", "line_number": 1, "line": "dummy", "severity": "LOW"}'


@pytest.mark.parametrize(
    ("verbose", "expected"),
    [
        (False, "dummy.j2:1 test rule 0 (test-rule-0)"),
        (
            True,
            RULE_TEXT_OUTPUT,
        ),
    ],
)
def test_to_rich(test_issue: LinterError, *, verbose: bool, expected: str) -> None:
    """Test the Rich string formats for LinterError."""
    assert str(test_issue.to_rich(verbose)) == expected


def test_to_json(test_issue: LinterError) -> None:
    """Test the json format for LinterError."""
    assert test_issue.to_json() == RULE_JSON_OUTPUT

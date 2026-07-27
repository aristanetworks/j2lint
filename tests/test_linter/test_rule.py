# Copyright (c) 2021-2026 Arista Networks, Inc.
# Use of this source code is governed by the MIT license
# that can be found in the LICENSE file.
"""Tests for j2lint.linter.rule.py."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any

import pytest

from j2lint.linter.error import LinterError

if TYPE_CHECKING:
    from collections.abc import Callable

    from j2lint.linter.rule import Rule

TEST_DATA_DIR = Path(__file__).parent / "data"


class TestRule:
    """Test j2lint.linter.rule.Rule."""

    def test__repr__(self, test_rule: Rule) -> None:
        """Test the Rule __repr__ format."""
        assert str(test_rule) == "T0: test rule 0"

    @pytest.mark.parametrize(
        ("checktext", "checkline", "filepath", "expected_errors_ids", "expected_logs"),
        [
            pytest.param(
                None,
                0,
                TEST_DATA_DIR / "test.j2",
                [],
                [],
                id="no error",
            ),
            pytest.param(
                None,
                1,
                TEST_DATA_DIR / "test.j2",
                [("T0", 42), ("T0", 42), ("T0", 42), ("T0", 42), ("T0", 42)],
                [],
                id="checkline rule error",
            ),
            pytest.param(
                2,
                None,
                TEST_DATA_DIR / "test.j2",
                [("T0", 42), ("T0", 42)],
                [],
                id="checktext rule error",
            ),
        ],
    )
    def test_checkrule(
        self,
        caplog: pytest.LogCaptureFixture,
        test_rule: Rule,
        make_issue_from_rule: Callable[[Rule], LinterError],
        checktext: int | None,
        checkline: int | None,
        filepath: str,
        expected_errors_ids: list[tuple[str, int]],
        expected_logs: list[str],
    ) -> None:
        """Test the Rule.checkrule method.

        TODO: This test is too complex and should be rewritten
        checktext and checkline values help selecting combination of possible rules.
        """

        def raise_notimplementederror(*args: Any, **kwargs: Any) -> None:
            raise NotImplementedError

        def return_empty_list(*args: Any, **kwargs: Any) -> list[Any]:  # noqa: ARG001
            return []

        caplog.set_level(logging.DEBUG)

        # Build checktext and checkline
        if checktext is None:
            test_rule.checktext = raise_notimplementederror  # type: ignore[reportAttributeAccessIssue]
        elif checktext == 0:
            test_rule.checktext = return_empty_list
        else:
            # checktext > 0
            test_rule.checktext = lambda *_: [make_issue_from_rule(test_rule) for _ in range(checktext)]  # type: ignore[reportAttributeAccessIssue]

        if checkline is None:
            test_rule.checkline = raise_notimplementederror  # type: ignore[reportAttributeAccessIssue]

        elif checkline == 0:
            test_rule.checkline = return_empty_list
        else:
            # checkline > 0
            test_rule.checkline = lambda *_args, **_kwargs: [make_issue_from_rule(test_rule) for _ in range(checkline)]  # type: ignore[reportAttributeAccessIssue]

        with Path(filepath).open(encoding="utf-8") as file_d:
            errors = test_rule.checkrule(filepath, file_d.read())
        errors_ids = [(error.rule.rule_id, error.line_number) for error in errors]
        assert errors_ids == expected_errors_ids
        assert caplog.record_tuples == expected_logs

    def test_checkrule_ignores_raw_block_content_for_line_rules(self, test_rule: Rule) -> None:
        """Test that line-based rules do not inspect content inside raw blocks."""

        def raise_notimplementederror(*args: Any, **kwargs: Any) -> None:
            raise NotImplementedError

        def checkline(filename: str, line: str, line_no: int) -> list[LinterError]:
            return [LinterError(line_no, line, filename, test_rule)] if "{{" in line else []

        test_rule.checktext = raise_notimplementederror  # type: ignore[reportAttributeAccessIssue]
        test_rule.checkline = checkline  # type: ignore[reportAttributeAccessIssue]

        text = "{% raw %}{{ hidden_value }}{% endraw %}\n{{ visible_value }}"
        errors = test_rule.checkrule("dummy.j2", text)

        assert [(error.line_number, error.line) for error in errors] == [(2, "{{ visible_value }}")]

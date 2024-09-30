# Copyright (c) 2021-2024 Arista Networks, Inc.
# Use of this source code is governed by the MIT license
# that can be found in the LICENSE file.
"""Tests for j2lint.linter.rule.py."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable

import pytest

if TYPE_CHECKING:
    from j2lint.linter.error import LinterError
    from j2lint.linter.rule import Rule

TEST_DATA_DIR = Path(__file__).parent / "data"


class TestRule:
    """Test j2lint.linter.rule.Rule."""

    def test__repr__(self, test_rule: Rule) -> None:
        """Test the Rule __repr__ format."""
        assert str(test_rule) == "T0: test rule 0"

    @pytest.mark.parametrize(
        ("checktext", "checkline", "file_path", "expected_errors_ids", "expected_logs"),
        [
            pytest.param(
                None,
                0,
                {"path": f"{TEST_DATA_DIR}/test.j2"},
                [],
                [],
                id="no error",
            ),
            pytest.param(
                None,
                1,
                {"path": f"{TEST_DATA_DIR}/test.j2"},
                [("T0", 42), ("T0", 42), ("T0", 42), ("T0", 42), ("T0", 42)],
                [],
                id="checkline rule error",
            ),
            pytest.param(
                2,
                None,
                {"path": "tests/test_linter/data/test.j2"},
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
        make_issue_from_rule: Callable[[int], list[LinterError]],
        checktext: None | int,
        checkline: None | int,
        file_path: dict[str, str],
        expected_errors_ids: list[tuple[str, int]],
        expected_logs: list[str],
    ) -> None:
        """Test the Rule.checkrule method.

        TODO: This text is too complex and should be rewritten
        checktext and checkline values help selecting combination of possible rules.
        """

        def raise_notimplementederror(*args: Any, **kwargs: Any) -> None:
            raise NotImplementedError

        def return_empty_list(*args: Any, **kwargs: Any) -> list[Any]:  # noqa: ARG001
            return []

        caplog.set_level(logging.DEBUG)

        # Build checktext and checkline
        if checktext is None:
            test_rule.checktext = raise_notimplementederror
        elif checktext == 0:
            test_rule.checktext = return_empty_list
        else:
            # checktext > 0
            test_rule.checktext = lambda *_: [issue for i in range(checktext) for issue in make_issue_from_rule(test_rule)]

        if checkline is None:
            test_rule.checkline = raise_notimplementederror

        elif checkline == 0:
            test_rule.checkline = return_empty_list
        else:
            # checkline > 0
            test_rule.checkline = lambda *_, line_no=0: [issue for i in range(checkline) for issue in make_issue_from_rule(test_rule)]  # noqa: ARG005

        with Path(file_path["path"]).open(encoding="utf-8") as file_d:
            errors = test_rule.checkrule(file_path, file_d.read())
        errors_ids = [(error.rule.rule_id, error.line_number) for error in errors]
        assert errors_ids == expected_errors_ids
        assert caplog.record_tuples == expected_logs

# Copyright (c) 2021-2026 Arista Networks, Inc.
# Use of this source code is governed by the MIT license
# that can be found in the LICENSE file.
"""Tests for GitHub workflow command serialization."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING
from unittest.mock import patch

import pytest

from j2lint.linter.error import LinterError
from j2lint.output import print_github_output

if TYPE_CHECKING:
    from collections.abc import Callable

    from j2lint.linter.rule import Rule


@pytest.mark.parametrize(("errors", "warnings"), [(0, 0), (1, 0), (0, 1), (2, 3)])
def test_github_levels_and_counts(capsys: pytest.CaptureFixture[str], make_issues: Callable[[int], list[LinterError]], errors: int, warnings: int) -> None:
    """Levels depend on classification, including LOW errors and HIGH warnings."""
    result = print_github_output({Path("dummy.j2"): make_issues(errors)}, {Path("dummy.j2"): make_issues(warnings)})
    assert result == (errors, warnings)
    expected = "".join(
        f"::{level} file=dummy.j2,line={index + 1},title=j2lint T{index}::test rule {index}\n"
        for level, count in (("error", errors), ("warning", warnings))
        for index in range(count)
    )
    captured = capsys.readouterr()
    assert captured.out == expected
    assert captured.err == ""


def test_github_escaping(capsys: pytest.CaptureFixture[str], test_rule: Rule) -> None:
    """Escape command separators and prevent messages from creating extra commands."""
    issue = LinterError(42, "unused source", "C:\\templates\\a,b:100%0A\r\n[é].j2", test_rule, "100%0A: value, [red]\r\n::error::injected")
    with patch.object(test_rule, "rule_id", "T0,:\r\n%0A"):
        print_github_output({Path("ignored-key.j2"): [issue]}, {})
    assert capsys.readouterr().out == (
        "::error file=C%3A\\templates\\a%2Cb%3A100%250A%0D%0A[é].j2,line=42,title=j2lint T0%2C%3A%0D%0A%250A::100%250A: value, [red]%0D%0A::error::injected\n"
    )


def test_github_stdin_and_file_locations(capsys: pytest.CaptureFixture[str], test_rule: Rule) -> None:
    """Only stdin findings lose their location when files and stdin are combined."""
    stdin_path = Path("/tmp/stdin.j2")  # noqa: S108
    issues = {
        stdin_path: [LinterError(1, "", str(stdin_path), test_rule)],
        Path("real.j2"): [LinterError(9, "", "real.j2", test_rule)],
    }
    assert print_github_output(issues, {}, stdin_filename=stdin_path) == (2, 0)
    assert capsys.readouterr().out == ("::error title=j2lint T0::test rule 0\n::error file=real.j2,line=9,title=j2lint T0::test rule 0\n")

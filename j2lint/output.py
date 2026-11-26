# Copyright (c) 2021-2026 Arista Networks, Inc.
# Use of this source code is governed by the MIT license
# that can be found in the LICENSE file.
"""Output GitHub Actions annotations for lint diagnostics."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

    from j2lint.linter.error import LinterError


def _escape_data(value: str) -> str:
    """Escape workflow command data, replacing percent signs first."""
    return value.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")


def _escape_property(value: str) -> str:
    """Escape workflow command properties, including their separators."""
    return _escape_data(value).replace(":", "%3A").replace(",", "%2C")


def print_github_output(
    lint_errors: dict[Path, list[LinterError]],
    lint_warnings: dict[Path, list[LinterError]],
    *,
    stdin_filename: Path | None = None,
) -> tuple[int, int]:
    """Write unwrapped annotations to stdout and return error and warning counts.

    Annotation levels follow the errors/warnings classification rather than rule
    severity. Stdin diagnostics omit locations because their temporary file is
    removed after linting.
    """
    totals = []
    for level, files in (("error", lint_errors), ("warning", lint_warnings)):
        total = 0
        for issues in files.values():
            for issue in issues:
                properties = []
                if stdin_filename is None or issue.filename != str(stdin_filename):
                    properties.extend((f"file={_escape_property(issue.filename)}", f"line={issue.line_number}"))
                properties.append(f"title={_escape_property(f'j2lint {issue.rule.rule_id}')}")
                sys.stdout.write(f"::{level} {','.join(properties)}::{_escape_data(issue.message)}\n")
                total += 1
        totals.append(total)
    return totals[0], totals[1]

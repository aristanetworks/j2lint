# Copyright (c) 2021-2026 Arista Networks, Inc.
# Use of this source code is governed by the MIT license
# that can be found in the LICENSE file.
"""Benchmark statement extraction and line-number calculation."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from j2lint.utils import get_jinja_statements

if TYPE_CHECKING:
    from pytest_codspeed import BenchmarkFixture


@pytest.mark.parametrize("indentation", [False, True], ids=["all-statements", "indentation"])
def test_get_jinja_statements(benchmark: BenchmarkFixture, statement_text: str, *, indentation: bool) -> None:
    """Measure multiline statement extraction at increasing template sizes."""
    statements = benchmark(get_jinja_statements, statement_text, indentation=indentation)

    count = statement_text.count("{%")
    assert len(statements) == count
    assert statements[0] == (" set value =\n    1 ", 2, 3, "{%", "%}")
    assert statements[-1] == (" set value =\n    1 ", 3 * count - 1, 3 * count, "{%", "%}")

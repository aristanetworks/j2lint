# Copyright (c) 2021-2026 Arista Networks, Inc.
# Use of this source code is governed by the MIT license
# that can be found in the LICENSE file.
"""Benchmark the complete built-in rule collection."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

    from pytest_codspeed import BenchmarkFixture

    from j2lint.linter.collection import RulesCollection


def test_lint_template(benchmark: BenchmarkFixture, collection: RulesCollection, template_file: Path, template_kind: str, block_count: int) -> None:
    """Measure file reading and all built-in rules, excluding input construction and terminal output."""
    errors, warnings = benchmark(collection.run, template_file)

    assert not warnings
    if template_kind == "errors":
        assert len(errors) == 2 * block_count
        assert {error.rule.rule_id for error in errors} == {"S1", "V1"}
    else:
        assert not errors

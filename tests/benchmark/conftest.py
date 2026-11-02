# Copyright (c) 2021-2026 Arista Networks, Inc.
# Use of this source code is governed by the MIT license
# that can be found in the LICENSE file.
"""Deterministic templates for j2lint performance benchmarks."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from j2lint.logger import logger

if TYPE_CHECKING:
    from pathlib import Path

CLEAN_BLOCK = """{# Benchmark template #}
{% for item in items %}
{%     if item.enabled %}
interface {{ item.name }}
 description {{ item.description | default('unset') }}
{%     endif %}
{% endfor %}
"""
RAW_BLOCK = """{% raw %}
{{UnlintedName}}
{% if hidden %}
{% endraw %}
"""


@pytest.fixture(autouse=True)
def disable_benchmark_logging(monkeypatch: pytest.MonkeyPatch) -> None:
    """Disable log output as in the default CLI, restoring it after each benchmark."""
    monkeypatch.setattr(logger, "disabled", True)


@pytest.fixture(params=[10, 100], ids=["10-blocks", "100-blocks"])
def block_count(request: pytest.FixtureRequest) -> int:
    """Return the number of repeated template blocks."""
    return request.param


@pytest.fixture(params=["clean", "errors", "raw"])
def template_kind(request: pytest.FixtureRequest) -> str:
    """Select valid templates, lint violations, or literal raw-block contents."""
    return request.param


@pytest.fixture
def template_file(tmp_path: Path, block_count: int, template_kind: str) -> Path:
    """Write the input outside the measured linting invocation."""
    block = CLEAN_BLOCK
    if template_kind == "errors":
        block = block.replace("{{ item.name }}", "{{ItemName}}")
    elif template_kind == "raw":
        block = RAW_BLOCK + block
    path = tmp_path / "benchmark.j2"
    path.write_text(block * block_count, encoding="utf-8")
    return path


@pytest.fixture(params=[100, 1000, 4000], ids=["100-statements", "1000-statements", "4000-statements"])
def statement_text(request: pytest.FixtureRequest) -> str:
    """Generate statements separated by template text to expose prefix-scan scaling."""
    return "plain template text\n{% set value =\n    1 %}\n" * request.param

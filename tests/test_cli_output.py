# Copyright (c) 2021-2026 Arista Networks, Inc.
# Use of this source code is governed by the MIT license
# that can be found in the LICENSE file.
"""Exercise output modes through the real CLI in isolated processes."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest


def invoke(*args: str, stdin: str | None = None, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    """Run the checked-out package without sharing logging state with pytest."""
    return subprocess.run(  # noqa: S603
        [sys.executable, "-m", "j2lint", *args],
        input=stdin,
        capture_output=True,
        text=True,
        check=False,
        cwd=Path(__file__).resolve().parents[1],
        env=env,
    )


@pytest.mark.parametrize(
    ("options", "levels", "exit_code"),
    [
        ([], ["error", "error"], 2),
        (["--warn", "V1", "--"], ["error", "warning"], 2),
        (["--warn", "S1", "V1", "--"], ["warning", "warning"], 0),
        (["--ignore", "S1", "V1", "--"], [], 0),
    ],
)
def test_github_rule_selection(tmp_path: Path, options: list[str], levels: list[str], exit_code: int) -> None:
    """Preserve warnings, ignored rules, exit codes, and paths with property separators."""
    template = tmp_path / "comma, colon: percent% unicode-é.j2"
    template.write_text("{{UPPER}}\n", encoding="utf-8")
    result = invoke("--output-format", "github", *options, str(template))
    assert result.returncode == exit_code, result.stderr
    lines = result.stdout.splitlines()
    assert [line.split(" ", 1)[0] for line in lines] == [f"::{level}" for level in levels]
    for line in lines:
        assert f"file={str(template).replace(',', '%2C').replace(':', '%3A').replace('percent%', 'percent%25')},line=1," in line
    assert result.stderr == ""


def test_github_clean_and_multiple_files(tmp_path: Path) -> None:
    """Emit only findings with their own locations, even in verbose mode."""
    clean = tmp_path / "clean.j2"
    clean.write_text("{{ value }}\n", encoding="utf-8")
    assert invoke("--output-format", "github", "--verbose", str(clean)).stdout == ""
    for name in ("one.j2", "two.j2"):
        (tmp_path / name).write_text("plain text\n{{value}}\n", encoding="utf-8")
    result = invoke("--output-format", "github", "--verbose", str(tmp_path))
    assert result.returncode == 2, result.stderr
    lines = result.stdout.splitlines()
    assert len(lines) == 2
    for name in ("one.j2", "two.j2"):
        assert any(line.startswith(f"::error file={tmp_path / name},line=2,title=j2lint S1::") for line in lines)
    assert result.stderr == ""


@pytest.mark.parametrize("logging_options", [[], ["--stdout", "--debug"]])
def test_github_raw_stdout(tmp_path: Path, logging_options: list[str]) -> None:
    """Long commands stay intact with forced color and a narrow terminal; logs use stderr."""
    template = tmp_path / "[red]long-file-name.j2"
    template.write_text("{{value}}\n", encoding="utf-8")
    result = invoke("--output-format", "github", *logging_options, str(template), env={**os.environ, "COLUMNS": "20", "FORCE_COLOR": "1"})
    assert result.returncode == 2, result.stderr
    assert result.stdout == (
        f"::error file={template},line=1,title=j2lint S1::"
        "A single space should be added between Jinja2 curly brackets and a variable name: {{ ethernet_interface }}\n"
    )
    if logging_options:
        assert "DEBUG" in result.stderr
    else:
        assert result.stderr == ""


def test_github_stdin_cleanup(tmp_path: Path) -> None:
    """Stdin annotations have no deleted-file link and leave no temporary files behind."""
    result = invoke("--output-format", "github", "--stdin", stdin="{{value}}\n", env={**os.environ, "TMPDIR": str(tmp_path)})
    assert result.returncode == 2, result.stderr
    assert result.stdout.startswith("::error title=j2lint S1::")
    assert len(result.stdout.splitlines()) == 1
    assert result.stderr == ""
    assert not list(tmp_path.iterdir())


def test_github_syntax_error(tmp_path: Path) -> None:
    """Syntax errors retain Jinja's specific diagnostic and the actual source line."""
    template = tmp_path / "syntax-error.j2"
    template.write_text("plain text\n{% if %}\n", encoding="utf-8")
    result = invoke("--output-format", "github", str(template))
    assert result.returncode == 2, result.stderr
    assert any(line.startswith(f"::error file={template},line=2,title=j2lint S0::Expected an expression") for line in result.stdout.splitlines())
    assert result.stderr == ""


@pytest.mark.parametrize(
    ("options", "message"),
    [
        (["--json", "--output-format", "github"], "not allowed with argument"),
        (["--output-format", "json", "-j"], "not allowed with argument"),
        (["--output-format", "text", "--json"], "not allowed with argument"),
        (["--list", "--output-format", "github"], "--list cannot be used with --output-format github"),
        (["--output-format", "unknown"], "invalid choice"),
    ],
)
def test_invalid_output_options(options: list[str], message: str) -> None:
    """Invalid option combinations explain the conflict on stderr without annotations."""
    result = invoke(*options)
    assert result.returncode == 2
    assert result.stdout == ""
    assert message in result.stderr


@pytest.mark.parametrize("listing", [False, True])
def test_json_output_alias(tmp_path: Path, *, listing: bool) -> None:
    """The new JSON selector preserves both diagnostics and rule listing output."""
    template = tmp_path / "error.j2"
    template.write_text("{{value}}\n", encoding="utf-8")
    options = ["--list"] if listing else [str(template)]
    legacy = invoke("--json", *options)
    selected = invoke("--output-format", "json", *options)
    assert selected.returncode == legacy.returncode == (0 if listing else 2)
    assert selected.stderr == legacy.stderr == ""
    assert json.loads(selected.stdout) == json.loads(legacy.stdout)


def test_explicit_text_output(tmp_path: Path) -> None:
    """Explicit text uses the existing human-readable output."""
    template = tmp_path / "error.j2"
    template.write_text("{{value}}\n", encoding="utf-8")
    default = invoke(str(template))
    selected = invoke("--output-format", "text", str(template))
    assert selected.returncode == default.returncode == 2
    assert selected.stdout == default.stdout
    assert selected.stderr == default.stderr == ""

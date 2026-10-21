# Copyright (c) 2021-2026 Arista Networks, Inc.
# Use of this source code is governed by the MIT license
# that can be found in the LICENSE file.
"""Regression tests for unchecked inputs and CLI failure reporting."""

# pylint: disable=redefined-outer-name

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import TYPE_CHECKING
from unittest.mock import patch

import pytest

from j2lint.cli import run
from j2lint.linter.error import InputError
from j2lint.utils import get_files

if TYPE_CHECKING:
    from collections.abc import Callable


@pytest.fixture(params=["module", "console"])
def invoke(request: pytest.FixtureRequest) -> Callable[..., subprocess.CompletedProcess[str]]:
    """Exercise both the module and the installed console script's entry function."""
    command = [sys.executable, "-m", "j2lint"]
    if request.param == "console":
        command = [sys.executable, "-c", "from j2lint.cli import run; raise SystemExit(run())"]

    def invoke_cli(*args: str, stdin: str | None = None) -> subprocess.CompletedProcess[str]:
        return subprocess.run(  # noqa: S603
            [*command, *args],
            input=stdin,
            capture_output=True,
            text=True,
            encoding="utf-8",
            cwd=Path(__file__).parent.parent,
            check=False,
            timeout=20,
        )

    return invoke_cli


@pytest.mark.parametrize("failure", ["missing", "missing-extensionless", "extension", "encoding"])
def test_input_failure_json(tmp_path: Path, invoke: Callable[..., subprocess.CompletedProcess[str]], failure: str) -> None:
    """Explicit unchecked inputs fail with a JSON diagnostic, even without logging."""
    path = tmp_path / "template.j2"
    if failure == "missing-extensionless":
        path = tmp_path / "missing"
    elif failure == "extension":
        path = tmp_path / "template.yaml"
        path.write_text("plain text", encoding="utf-8")
    elif failure == "encoding":
        path.write_bytes(b"\xff")

    result = invoke("--json", str(path))

    assert result.returncode == 1
    assert not result.stderr
    payload = json.loads(result.stdout)
    assert payload["WARNINGS"] == []
    assert len(payload["ERRORS"]) == 1
    error = payload["ERRORS"][0]
    assert error["id"] == "E0"
    assert error["filename"] == str(path)
    assert error["line_number"] == 0
    assert error["line"] == ""
    assert error["severity"] == "HIGH"
    assert error["message"]
    if failure == "extension":
        assert "--extensions" in error["message"]
    elif failure == "encoding":
        assert "UTF-8" in error["message"]


def test_input_failure_text(tmp_path: Path, invoke: Callable[..., subprocess.CompletedProcess[str]]) -> None:
    """Human output explains the failure without requiring --log."""
    result = invoke(str(tmp_path / "missing.j2"))
    assert result.returncode == 1
    assert "Could not access path" in " ".join(result.stdout.split())
    assert "E0" in result.stdout
    assert "Traceback" not in result.stdout + result.stderr


def test_other_inputs_are_checked(tmp_path: Path, invoke: Callable[..., subprocess.CompletedProcess[str]]) -> None:
    """Both discovery and read failures leave remaining inputs eligible for linting."""
    missing = tmp_path / "missing.j2"
    invalid = tmp_path / "invalid.j2"
    invalid.write_bytes(b"\xff")
    linted = tmp_path / "linted.j2"
    linted.write_text("{{Bad}}", encoding="utf-8")

    result = invoke("--json", str(missing), str(tmp_path), str(invalid), str(linted))

    assert result.returncode == 1
    errors = json.loads(result.stdout)["ERRORS"]
    assert {error["filename"] for error in errors} == {str(missing), str(invalid), str(linted)}
    assert [error["id"] for error in errors].count("E0") == 2
    assert {error["id"] for error in errors} >= {"S1", "V1"}


def test_directory_filtering(tmp_path: Path, invoke: Callable[..., subprocess.CompletedProcess[str]]) -> None:
    """Empty directories and unmatched files remain valid directory scans."""
    assert invoke("--json", str(tmp_path)).returncode == 0
    (tmp_path / "not-a-template.yaml").write_bytes(b"\xff")
    result = invoke("--json", str(tmp_path))
    assert result.returncode == 0
    assert json.loads(result.stdout) == {"ERRORS": [], "WARNINGS": []}
    (tmp_path / "template.j2").write_text("{{Bad}}", encoding="utf-8")
    result = invoke("--json", str(tmp_path))
    assert result.returncode == 2
    assert {error["id"] for error in json.loads(result.stdout)["ERRORS"]} == {"S1", "V1"}


def test_custom_extension_and_stdin(tmp_path: Path, invoke: Callable[..., subprocess.CompletedProcess[str]]) -> None:
    """Extension overrides work for files without excluding extensionless STDIN."""
    path = tmp_path / "template.yaml"
    path.write_text("{{Bad}}", encoding="utf-8")
    result = invoke("--json", "--extensions", "yaml", str(path))
    assert result.returncode == 2
    assert {error["id"] for error in json.loads(result.stdout)["ERRORS"]} == {"S1", "V1"}
    result = invoke("--json", "--extensions", "yaml", "--stdin", stdin="{{Bad}}")
    assert result.returncode == 2
    errors = json.loads(result.stdout)["ERRORS"]
    assert {error["id"] for error in errors} == {"S1", "V1"}
    assert not Path(errors[0]["filename"]).exists()


def test_json_with_console_logs(tmp_path: Path, invoke: Callable[..., subprocess.CompletedProcess[str]]) -> None:
    """Console logs cannot corrupt machine-readable diagnostics."""
    result = invoke("--json", "--stdout", "--debug", str(tmp_path / "missing.j2"))
    assert result.returncode == 1
    assert json.loads(result.stdout)["ERRORS"][0]["id"] == "E0"
    assert "DEBUG" in result.stderr


def test_directory_scan_error(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """os.walk errors must be surfaced rather than silently skipping subtrees."""

    def fail_walk(_path: str, *, onerror: Callable[[OSError], None]) -> list[tuple[str, list[str], list[str]]]:
        onerror(PermissionError(13, "Permission denied", str(tmp_path / "inaccessible")))
        return []

    monkeypatch.setattr("j2lint.utils.os.walk", fail_walk)
    with pytest.raises(InputError, match="Could not scan directory: Permission denied"):
        get_files([tmp_path], [".j2"])


def test_read_permission_error(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Permission errors propagate through Runner to the CLI diagnostic output."""
    path = tmp_path / "template.j2"
    path.touch()
    with patch.object(Path, "open", side_effect=PermissionError(13, "Permission denied")):
        result = run(["--json", str(path)])
    assert result == 1
    assert "Permission denied" in json.loads(capsys.readouterr().out)["ERRORS"][0]["message"]


def test_stdin_cleanup_on_exception(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Unexpected failures must also remove the STDIN temporary file."""
    monkeypatch.setattr("j2lint.cli.tempfile.tempdir", str(tmp_path))
    with patch("sys.stdin") as stdin, patch("j2lint.cli.get_linting_issues", side_effect=RuntimeError("unexpected")):
        stdin.isatty.return_value = False
        stdin.read.return_value = "plain text"
        with pytest.raises(RuntimeError, match="unexpected"):
            run(["--stdin"])
    assert not list(tmp_path.iterdir())


def test_unexpected_module_failure() -> None:
    """Unexpected exceptions must exit nonzero and leave traceback output on stderr."""
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "import runpy; from unittest.mock import patch; "
                "\nwith patch('j2lint.cli.run', side_effect=RuntimeError('unexpected')):"
                "\n    runpy.run_module('j2lint', run_name='__main__')"
            ),
        ],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent,
        check=False,
        timeout=20,
    )
    assert result.returncode == 1
    assert not result.stdout
    assert "RuntimeError" in result.stderr

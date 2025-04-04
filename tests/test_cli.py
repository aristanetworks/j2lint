# Copyright (c) 2021-2025 Arista Networks, Inc.
# Use of this source code is governed by the MIT license
# that can be found in the LICENSE file.
"""Tests for j2lint.cli.py."""

from __future__ import annotations

import logging
import re
from argparse import Namespace
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable
from unittest.mock import patch

import pytest
from rich.console import ConsoleDimensions

import j2lint
from j2lint import CONSOLE
from j2lint.cli import (
    create_parser,
    print_json_output,
    print_string_output,
    run,
    sort_issues,
)

from .utils import (
    NO_ERROR_NO_WARNING_JSON,
    ONE_ERROR,
    ONE_ERROR_JSON,
    ONE_ERROR_ONE_WARNING_JSON,
    ONE_ERROR_ONE_WARNING_VERBOSE,
    ONE_ERROR_REGEX,
    ONE_WARNING_VERBOSE,
    does_not_raise,
    j2lint_default_rules_string,
)

if TYPE_CHECKING:
    from collections.abc import Generator

    from j2lint.linter.error import LinterError

# Fixed size console for tests output
CONSOLE.size = ConsoleDimensions(width=80, height=74)


@pytest.mark.parametrize(
    ("argv", "namespace_modifications"),
    [
        (pytest.param([], {"extensions": [".j2", ".jinja", ".jinja2"]}, id="default")),
        pytest.param(
            ["--log", "--stdout", "-j", "-d", "-v", "--stdin", "--version"],
            {
                "debug": True,
                "stdout": True,
                "stdin": True,
                "version": True,
                "log": True,
                "json": True,
                "verbose": True,
                "extensions": [".j2", ".jinja", ".jinja2"],
            },
            id="set all debug flags",
        ),
    ],
)
def test_create_parser(default_namespace: Namespace, argv: list[str], namespace_modifications: dict[str, Any]) -> None:
    """Test j2lint.cli.create_parser.

    the namespace_modifications is a dictionary where key
    is one of the keys in the namespace and value is the value
    it should be overwritten to.

    This test only verifies that given a set of arguments on the
    cli, the parser returns the correct values in the Namespace
    """
    expected_namespace = default_namespace
    for key, value in namespace_modifications.items():
        setattr(expected_namespace, key, value)
    parser = create_parser()
    options = parser.parse_args(argv)
    assert options == expected_namespace


@pytest.mark.parametrize(
    ("number_issues", "issues_modifications", "expected_sorted_issues_ids"),
    [
        (0, {}, []),
        (1, {}, [("dummy.j2", "T0", 1, "test-rule-0")]),
        pytest.param(
            2,
            {},
            [
                ("dummy.j2", "T0", 1, "test-rule-0"),
                ("dummy.j2", "T1", 2, "test-rule-1"),
            ],
            id="sort-on-linenumber",
        ),
        pytest.param(
            2,
            {2: {"filename": "aaa.j2"}},
            [("aaa.j2", "T1", 2, "test-rule-1"), ("dummy.j2", "T0", 1, "test-rule-0")],
            id="sort-on-filename",
        ),
        pytest.param(
            2,
            {2: {"rule": {"rule_id": "AA"}, "line_number": 1}},
            [
                ("dummy.j2", "AA", 1, "test-rule-1"),
                ("dummy.j2", "T0", 1, "test-rule-0"),
            ],
            id="sort-on-rule-id",
        ),
    ],
)
def test_sort_issues(
    make_issues: Callable[[int], list[LinterError]],
    number_issues: int,
    issues_modifications: dict[int, dict[str, Any]],
    expected_sorted_issues_ids: list[tuple[Any]],
) -> None:
    """Test j2lint.cli.sort_issues.

    the issues_modificartions is a dictionary that has the following
    structure:

      { <issue-index>: { <key>: <desired_value }

    the test will go over these modifications and apply them to the
    appropriate issues, apply the sort_issues method and verifies the
    ordering is correct
    """
    issues = make_issues(number_issues)

    # In the next step we apply modifications on the generated LinterErrors
    # if required
    for index, modification in issues_modifications.items():
        for key, value in modification.items():
            if isinstance(value, dict):
                nested_obj = getattr(issues[index - 1], key)
                for n_key, n_value in value.items():
                    setattr(nested_obj, n_key, n_value)
            else:
                setattr(issues[index - 1], key, value)
    sorted_issues = sort_issues(issues)
    sorted_issues_ids = [
        (
            issue.filename,
            issue.rule.rule_id,
            issue.line_number,
            issue.rule.short_description,
        )
        for issue in sorted_issues
    ]
    assert sorted_issues_ids == expected_sorted_issues_ids


@pytest.mark.parametrize(
    ("options", "number_errors", "number_warnings", "expected_output", "expected_stdout"),
    [
        pytest.param(
            Namespace(verbose=False),
            0,
            0,
            (0, 0),
            "",
            id="No issue - cli",
        ),
        pytest.param(
            Namespace(verbose=True),
            0,
            0,
            (0, 0),
            "Linting complete. No problems found!\n",
            id="No issue - cli",
        ),
        pytest.param(
            Namespace(verbose=False),
            1,
            0,
            (1, 0),
            ONE_ERROR,
            id="One error - cli",
        ),
        pytest.param(
            Namespace(verbose=True),
            0,
            1,
            (0, 1),
            ONE_WARNING_VERBOSE,
            id="One warning - cli",
        ),
    ],
)
def test_print_string_output(
    capsys: pytest.LogCaptureFixture,
    make_issues: Callable[[int], list[LinterError]],
    options: Namespace,
    number_errors: int,
    number_warnings: int,
    expected_output: tuple[int, int],
    expected_stdout: str,
) -> None:
    """Test j2lint.cli.print_string_output."""
    errors = {"dummy.j2": make_issues(number_errors)}
    warnings = {"dummy.j2": make_issues(number_warnings)}
    total_errors, total_warnings = print_string_output(errors, warnings, verbose=options.verbose)

    assert total_errors == expected_output[0]
    assert total_warnings == expected_output[1]

    captured = capsys.readouterr()
    assert captured.out == expected_stdout


@pytest.mark.parametrize(
    ("number_errors", "number_warnings", "expected_output", "expected_stdout"),
    [
        pytest.param(0, 0, (0, 0), NO_ERROR_NO_WARNING_JSON, id="No issue - json"),
        pytest.param(1, 0, (1, 0), ONE_ERROR_JSON, id="one error - json"),
        pytest.param(1, 1, (1, 1), ONE_ERROR_ONE_WARNING_JSON, id="one error and one warning - json"),
    ],
)
def test_print_json_output(
    capsys: pytest.Fixture,
    make_issues: pytest.Fixture,
    number_errors: int,
    number_warnings: int,
    expected_output: tuple[int, int],
    expected_stdout: str,
) -> None:
    """Test j2lint.cli.print_json_output."""
    errors = {"ERRORS": make_issues(number_errors)}
    warnings = {"WARNINGS": make_issues(number_warnings)}
    total_errors, total_warnings = print_json_output(errors, warnings)

    assert total_errors == expected_output[0]
    assert total_warnings == expected_output[1]

    captured = capsys.readouterr()
    assert captured.out == expected_stdout


@pytest.mark.parametrize(
    ("argv", "expected_stdout", "expected_stderr", "expected_exit_code", "expected_raise", "number_errors", "number_warnings"),
    [
        pytest.param([], "", "HELP", 1, does_not_raise(), 0, 0, id="no input"),
        pytest.param(["-h"], "HELP", "", 0, pytest.raises(SystemExit), 0, 0, id="help"),
        pytest.param(
            ["--version"],
            "Jinja2-Linter Version v1.2.0\n",
            "",
            0,
            does_not_raise(),
            0,
            0,
            id="version",
        ),
        pytest.param(
            ["--log", "tests/data/test.j2"],
            "",
            "",
            0,
            does_not_raise(),
            0,
            0,
            id="log level INFO",
        ),
        pytest.param(
            ["-v", "tests/data/test.j2"],
            ONE_ERROR_ONE_WARNING_VERBOSE,
            "",
            2,
            does_not_raise(),
            1,
            1,
            id="one error and one warning - verbose",
        ),
        pytest.param(
            ["-j", "tests/data/test.j2"],
            ONE_ERROR_ONE_WARNING_JSON,
            "",
            2,
            does_not_raise(),
            1,
            1,
            id="one error and one warning - json",
        ),
        pytest.param(
            ["-l"],
            "DEFAULT_RULES",
            "",
            0,
            does_not_raise(),
            0,
            0,
            id="list rules",
        ),
        pytest.param(
            ["--stdout", "--debug", "tests/data/test.j2"],
            "",
            "",
            0,
            does_not_raise(),
            0,
            0,
            id="log level DEBUG",
        ),
        pytest.param(
            ["--stdout", "tests/data/test.j2"],
            "",
            "",
            0,
            does_not_raise(),
            0,
            0,
            id="o / stdout",
        ),
    ],
)
def test_run(
    capsys: pytest.Fixture,
    caplog: pytest.Fixture,
    j2lint_usage_string: str,
    make_issues: pytest.Fixture,
    argv: list[str],
    expected_stdout: str,
    expected_stderr: str,
    expected_exit_code: int,
    expected_raise: Generator,
    number_errors: int,
    number_warnings: int,
) -> None:
    """Test the j2lint.cli.run method.

    This test is a bit too complex and should probably be split out to test various
    functionalities

    the call is to test the various options of the main entry point, patching away inner
    methods when required. The id of the tests explains the intention.
    """
    if "-o" in argv or "--stdout" in argv:
        caplog.set_level(logging.INFO)
    if "-d" in argv or "--debug" in argv:
        caplog.set_level(logging.DEBUG)
    # TODO: this method needs to be split a bit as it has too many responsibility
    if expected_stdout == "HELP":
        expected_stdout = j2lint_usage_string
    if expected_stdout == "DEFAULT_RULES":
        expected_stdout = j2lint_default_rules_string()
    if expected_stderr == "HELP":
        expected_stderr = j2lint_usage_string
    with expected_raise, patch("j2lint.cli.Runner.run") as mocked_runner_run, patch("logging.disable"):
        mocked_runner_run.return_value = (
            make_issues(number_errors),
            make_issues(number_warnings),
        )
        run_return_value = run(argv)
        captured = capsys.readouterr()
        if "-o" not in argv and "--stdout" not in argv:
            assert str(captured.out) == expected_stdout
            assert captured.out == expected_stdout
            # Hmm - WHY - need to find why failing with stdout
            assert captured.err == expected_stderr
        else:
            assert expected_stdout in captured.out
        assert run_return_value == expected_exit_code
        if ("-o" in argv or "--stdout" in argv) and ("-d" in argv or "--debug" in argv):
            assert "DEBUG" in [record.levelname for record in caplog.records]


def test_run_stdin(capsys: pytest.LogCaptureFixture) -> None:
    """Test j2lint.cli.run when using stdin.

    Note that the code is checking that this is not run from a tty

    A solution to run is something like:

    ```
    cat myfile.j2 | j2lint --stdin
    ```

    In this test, the isatty answer is mocked.
    """
    with (
        patch("sys.stdin") as patched_stdin,
        patch.object(j2lint.cli.Path, "unlink", side_effect=j2lint.cli.Path.unlink, autospec=True) as mocked_os_unlink,
        patch("logging.disable"),
    ):
        patched_stdin.isatty.return_value = False
        patched_stdin.read.return_value = "{%set test=42 %}"
        run_return_value = run(["--log", "--stdin"])
        patched_stdin.isatty.assert_called_once()
        captured = capsys.readouterr()
        normalized_string = " ".join(captured.out.split())
        matches = re.search(
            ONE_ERROR_REGEX,
            normalized_string,
            re.MULTILINE,
        )
        assert matches is not None
        path = Path(matches.groups()[0])
        mocked_os_unlink.assert_called_with(path)
        assert path.exists() is False
        assert run_return_value == 2

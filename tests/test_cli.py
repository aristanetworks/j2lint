"""
Tests for j2lint.cli.py
"""
import logging
import os
import re
from unittest.mock import patch
from argparse import Namespace

import pytest

from j2lint.cli import print_string_output, print_json_output, sort_issues, create_parser, run, RULES_DIR

from .utils import does_not_raise, j2lint_default_rules_string


@pytest.fixture
def default_namespace():
    """
    Default ArgPase namespace for j2lint
    """
    return Namespace(
        files=[],
        ignore=[],
        warn=[],
        list=False,
        rules_dir=[RULES_DIR],
        verbose=False,
        debug=False,
        json=False,
        stdin=False,
        log=False,
        version=False,
        stdout=False,
    )


@pytest.mark.parametrize(
    "argv, namespace_modifications",
    [
        (pytest.param([], {}, id="default")),
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
            },
            id="set all debug flags",
        ),
    ],
)
def test_create_parser(default_namespace, argv, namespace_modifications):
    """
    Test j2lint.cli.create_parser

    the namespace_modifications is a dictionnary where key
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
    "number_issues, issues_modifications, expected_sorted_issues_ids",
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
            [("aaa.j2", "T1", 2, "test-rule-1"),
             ("dummy.j2", "T0", 1, "test-rule-0")],
            id="sort-on-filename",
        ),
        pytest.param(
            2,
            {2: {"rule": {"id": "AA"}, "line_number": 1}},
            [
                ("dummy.j2", "AA", 1, "test-rule-1"),
                ("dummy.j2", "T0", 1, "test-rule-0"),
            ],
            id="sort-on-rule-id",
        ),
    ],
)
def test_sort_issues(
        make_issues, number_issues, issues_modifications, expected_sorted_issues_ids
):
    """
    Test j2lint.cli.sort_issues

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
        (issue.filename, issue.rule.id,
         issue.line_number, issue.rule.short_description)
        for issue in sorted_issues
    ]
    assert sorted_issues_ids == expected_sorted_issues_ids


@pytest.mark.parametrize(
    "options, number_errors, number_warnings, expected_output, expected_stdout",
    [
        pytest.param(
            Namespace(verbose=False), 0, 0, (0, 0), "\nLinting complete. No problems found.\n", id="No issue - cli"
        ),
        pytest.param(
            Namespace(verbose=True), 0, 0, (0, 0), "\nLinting complete. No problems found.\n", id="No issue - cli"
        ),
        pytest.param(
            Namespace(verbose=False),
            1,
            0,
            (1, 0),
            "\nJINJA2 LINT ERRORS\n************ File ERRORS\ndummy.j2:1 test rule 0 (test-rule-0)\n\n"
            "Jinja2 linting finished with 1 error(s) and 0 warning(s)\n",
            id="One error - cli",
        ),
        pytest.param(
            Namespace(verbose=True),
            0,
            1,
            (0, 1),
            """
JINJA2 LINT WARNINGS
************ File WARNINGS
Linting rule: T0
Rule description: test rule 0
Error line: dummy.j2:1 dummy
Error message: test rule 0


Jinja2 linting finished with 0 error(s) and 1 warning(s)
""",
            id="One warning - cli",
        ),
    ],
)
def test_print_string_output(
        capsys,
        make_issues,
        options,
        number_errors,
        number_warnings,
        expected_output,
        expected_stdout,
):
    """
    Test j2lint.cli.print_string_output
    """

    errors = {"ERRORS": make_issues(number_errors)}
    warnings = {"WARNINGS": make_issues(number_warnings)}
    total_errors, total_warnings = print_string_output(
        errors, warnings, options.verbose)

    assert total_errors == expected_output[0]
    assert total_warnings == expected_output[1]

    captured = capsys.readouterr()
    assert captured.out == expected_stdout


@pytest.mark.parametrize(
    "number_errors, number_warnings, expected_output, expected_stdout",
    [
        pytest.param(
            0, 0, (0, 0), '\n{"ERRORS": [], "WARNINGS": []}\n', id="No issue - json"),
        pytest.param(1, 0, (1, 0), '\n{"ERRORS": [{"id": "T0", "message": "test rule 0", '
                                   '"filename": "dummy.j2", "line_number": 1, '
                     '"line": "dummy", "severity": "LOW"}], "WARNINGS": []}\n', id="one error - json"),
        pytest.param(1, 1, (1, 1), '\n{"ERRORS": [{"id": "T0", "message": "test rule 0", '
                                   '"filename": "dummy.j2", "line_number": 1, '
                     '"line": "dummy", "severity": "LOW"}], "WARNINGS": [{"id": "T0", "message": "test rule 0", '
                     '"filename": "dummy.j2", "line_number": 1, "line": "dummy", "severity": "LOW"}]}\n',
                     id="one error and one warnings - json"),
    ],
)
def test_print_json_output(
        capsys,
        make_issues,
        number_errors,
        number_warnings,
        expected_output,
        expected_stdout,
):
    """
        Test j2lint.cli.print_json_output
    """

    errors = {"ERRORS": make_issues(number_errors)}
    warnings = {"WARNINGS": make_issues(number_warnings)}
    total_errors, total_warnings = print_json_output(errors, warnings)

    assert total_errors == expected_output[0]
    assert total_warnings == expected_output[1]

    captured = capsys.readouterr()
    print(captured)
    assert captured.out == expected_stdout


@pytest.mark.parametrize(
    "argv, expected_stdout, expected_stderr, expected_exit_code, expected_raise, number_errors, number_warnings",
    [
        pytest.param([], "", "HELP", 1, does_not_raise(), 0, 0, id="no input"),
        pytest.param(["-h"], "HELP", "", 0,
                     pytest.raises(SystemExit), 0, 0, id="help"),
        pytest.param(
            ["--version"],
            "Jinja2-Linter Version v1.0.0\n",
            "",
            0,
            does_not_raise(),
            0,
            0,
            id="version",
        ),
        pytest.param(
            ["--log", "tests/data/test.j2"],
            "\nLinting complete. No problems found.\n",
            "",
            0,
            does_not_raise(),
            0,
            0,
            id="log level INFO",
        ),
        pytest.param(
            ["-v", "tests/data/test.j2"],
            """
JINJA2 LINT ERRORS
************ File tests/data/test.j2
Linting rule: T0
Rule description: test rule 0
Error line: dummy.j2:1 dummy
Error message: test rule 0


JINJA2 LINT WARNINGS
************ File tests/data/test.j2
Linting rule: T0
Rule description: test rule 0
Error line: dummy.j2:1 dummy
Error message: test rule 0


Jinja2 linting finished with 1 error(s) and 1 warning(s)
""",
            "",
            2,
            does_not_raise(),
            1,
            1,
            id="verbose, one error, one warning",
        ),
        pytest.param(
            ["-j", "tests/data/test.j2"],
            '\n{"ERRORS": '
            '[{"id": "T0", "message": "test rule 0", "filename": "dummy.j2", "line_number": 1, "line": "dummy", "severity": "LOW"}], '
            '"WARNINGS": '
            '[{"id": "T0", "message": "test rule 0", "filename": "dummy.j2", "line_number": 1, "line": "dummy", "severity": "LOW"}]'
            "}\n",
            "",
            2,
            does_not_raise(),
            1,
            1,
            id="json, one error, one warning",
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
            "Linting complete. No problems found.\n",
            "",
            0,
            does_not_raise(),
            0,
            0,
            id="log level DEBUG",
        ),
        pytest.param(
            ["--stdout", "tests/data/test.j2"],
            "Linting complete. No problems found.\n",
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
        capsys,
        caplog,
        j2lint_usage_string,
        make_issues,
        argv,
        expected_stdout,
        expected_stderr,
        expected_exit_code,
        expected_raise,
        number_errors,
        number_warnings,
):
    """
    Test the j2lint.cli.run method

    This test is a bit too complex and should probably be splitted out to test various
    functionalities

    the call is to test the various options of the main entry point, patching away inner
    methods when required. The id of the tests explains the intention.
    """
    if "-o" in argv or "--stdout" in argv:
        caplog.set_level(logging.INFO)
    if "-d" in argv or "--debug" in argv:
        caplog.set_level(logging.DEBUG)
    # TODO this method needs to be split a bit as it has
    # too many responsibility
    if expected_stdout == "HELP":
        expected_stdout = j2lint_usage_string
    if expected_stdout == "DEFAULT_RULES":
        expected_stdout = j2lint_default_rules_string()
    if expected_stderr == "HELP":
        expected_stderr = j2lint_usage_string
    with expected_raise:
        with patch("j2lint.cli.Runner.run") as mocked_runner_run, patch(
            "logging.disable"
        ):
            errors = {"ERRORS": make_issues(number_errors)}
            warnings = {"WARNINGS": make_issues(number_warnings)}
            mocked_runner_run.return_value = (
                errors["ERRORS"], warnings["WARNINGS"])
            run_return_value = run(argv)
            captured = capsys.readouterr()
            if "-o" not in argv and "--stdout" not in argv:
                assert captured.out == expected_stdout
                # Hmm - WHY - need to find why failing with stdout
                assert captured.err == expected_stderr
            else:
                assert expected_stdout in captured.out
            assert run_return_value == expected_exit_code
            if ("-o" in argv or "--stdout" in argv) and (
                    "-d" in argv or "--debug" in argv
            ):
                assert "DEBUG" in [
                    record.levelname for record in caplog.records]


def test_run_stdin(capsys):
    """
    Test j2lint.cli.run when using stdin
    Note that the code is checking that this is not run from a tty

    A solution to run is something like:
    ```
    cat myfile.j2 | j2lint --stdin
    ```

    In this test, the isatty answer is mocked.
    """
    with patch("sys.stdin") as patched_stdin, patch(
        "os.unlink", side_effect=os.unlink
    ) as mocked_os_unlink, patch("logging.disable"):
        patched_stdin.isatty.return_value = False
        patched_stdin.read.return_value = "{%set test=42 %}"
        run_return_value = run(["--log", "--stdin"])
        patched_stdin.isatty.assert_called_once()
        captured = capsys.readouterr()
        matches = re.match(
            r"\nJINJA2 LINT ERRORS\n\*\*\*\*\*\*\*\*\*\*\*\* File \/.*\n(\/.*.j2):1 "
            r"Jinja statement should have a single space before and after: '{% statement %}' "
            r"\(jinja-statements-single-space\)\n\nJinja2 linting finished with 1 error\(s\) "
            r"and 0 warning\(s\)\n",
            captured.out,
            re.MULTILINE,
        )
        assert matches is not None
        mocked_os_unlink.assert_called_with(matches.groups()[0])
        assert os.path.exists(matches.groups()[0]) is False
        assert run_return_value == 2

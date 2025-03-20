# Copyright (c) 2021-2025 Arista Networks, Inc.
# Use of this source code is governed by the MIT license
# that can be found in the LICENSE file.
"""cli.py - Command line argument parser."""

from __future__ import annotations

import argparse
import json
import logging
import sys
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING

from rich.tree import Tree

from j2lint import CONSOLE, DESCRIPTION, NAME, VERSION
from j2lint.linter.collection import DEFAULT_RULE_DIR, RulesCollection
from j2lint.linter.runner import Runner
from j2lint.logger import add_handler, logger
from j2lint.utils import get_files

if TYPE_CHECKING:
    from .linter.error import LinterError

IGNORE_RULES = WARN_RULES = [
    "jinja-syntax-error",
    "single-space-decorator",
    "operator-enclosed-by-spaces",
    "jinja-statements-single-space",
    "jinja-statements-indentation",
    "jinja-statements-no-tabs",
    "single-statement-per-line",
    "jinja-statements-delimiter",
    "jinja-variable-lower-case",
    "jinja-variable-format",
    "S0",
    "S1",
    "S2",
    "S3",
    "S4",
    "S5",
    "S6",
    "S7",
    "V1",
    "V2",
]


def create_parser() -> argparse.ArgumentParser:
    """Initialize a new argument parser object.

    Returns
    -------
    ArgumentParser
        Argument parser object
    """
    parser = argparse.ArgumentParser(prog=NAME, description=DESCRIPTION)

    parser.add_argument(
        dest="files",
        metavar="FILE",
        nargs="*",
        default=[],
        help="files or directories to lint",
    )
    parser.add_argument("-l", "--list", default=False, action="store_true", help="list of lint rules")
    parser.add_argument(
        "-r",
        "--rules_dir",
        dest="rules_dir",
        action="append",
        default=[DEFAULT_RULE_DIR],
        help="rules directory",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        default=False,
        action="store_true",
        help="verbose output for lint issues",
    )
    parser.add_argument(
        "-e",
        "--extensions",
        default="j2,jinja,jinja2",
        help="comma delimited list of file extensions, default is 'j2,jinja,jinja2'",
        type=lambda s: [f".{item}" for item in s.split(",")],
    )
    parser.add_argument("-d", "--debug", default=False, action="store_true", help="enable debug logs")
    parser.add_argument("-j", "--json", default=False, action="store_true", help="enable JSON output")
    parser.add_argument(
        "-s",
        "--stdin",
        default=False,
        action="store_true",
        help="accept template from STDIN",
    )
    parser.add_argument("--log", default=False, action="store_true", help="enable logging")
    parser.add_argument("--version", default=False, action="store_true", help="Version of j2lint")
    parser.add_argument("-o", "--stdout", default=False, action="store_true", help="stdout logging")
    parser.add_argument(
        "-i",
        "--ignore",
        nargs="*",
        choices=IGNORE_RULES,
        default=[],
        help="rules to ignore, use `--` after this option to enter FILES",
    )
    parser.add_argument(
        "-w",
        "--warn",
        nargs="*",
        choices=WARN_RULES,
        default=[],
        help="rules to warn, use `--` after this option to enter FILES",
    )

    return parser


def sort_issues(issues: list[LinterError]) -> list[LinterError]:
    """Sorted list of issues.

    Parameters
    ----------
    issues
        List of issue dictionaries

    Returns
    -------
    list
        List of sorted issue dictionaries
    """
    issues.sort(key=lambda issue: (issue.filename, issue.line_number, issue.rule.rule_id))
    return issues


def get_linting_issues(
    files: list[Path], collection: RulesCollection, checked_files: list[Path]
) -> tuple[dict[Path, list[LinterError]], dict[Path, list[LinterError]]]:
    """Check errors and warnings.

    Parameters
    ----------
    files
        List of files.
    collection
        The RulesCollection to use on the file.
    checked_files
        List of files already checked.

    Returns
    -------
    tuple[dict[Path, list[LinterError]], dict[Path, list[LinterError]]]
        A two tuple containing two dictionaries. The first dictionary contains the errors and the second dictionary the warnings.
    """
    lint_errors: dict[Path, list[LinterError]] = {}
    lint_warnings: dict[Path, list[LinterError]] = {}

    # Get linting issues
    for file_name in files:
        runner = Runner(collection, file_name, checked_files)
        if file_name not in lint_errors:
            lint_errors[file_name] = []
        if file_name not in lint_warnings:
            lint_warnings[file_name] = []
        j2_errors, j2_warnings = runner.run()
        lint_errors[file_name].extend(sort_issues(j2_errors))
        lint_warnings[file_name].extend(sort_issues(j2_warnings))
    return lint_errors, lint_warnings


def print_json_output(
    lint_errors: dict[Path, list[LinterError]],
    lint_warnings: dict[Path, list[LinterError]],
) -> tuple[int, int]:
    """Print json output.

    Parameters
    ----------
    lint_errors
        a dictionary containing pairs of type {filename: list of errors}
    lint_warnings
        a dictionary containing pairs of type {filename: list of warnings}

    Returns
    -------
    tuple[int, int]
        A two tuple containing the total number of errors and the total number of warnings.
    """
    json_output: dict[str, list[str]] = {"ERRORS": [], "WARNINGS": []}
    for errors in lint_errors.values():
        for error in errors:
            json_output["ERRORS"].append(json.loads(str(error.to_json())))
    for warnings in lint_warnings.values():
        for warning in warnings:
            json_output["WARNINGS"].append(json.loads(str(warning.to_json())))
    CONSOLE.print_json(f"\n{json.dumps(json_output)}")

    return len(json_output["ERRORS"]), len(json_output["WARNINGS"])


def print_string_output(
    lint_errors: dict[Path, list[LinterError]],
    lint_warnings: dict[Path, list[LinterError]],
    *,
    verbose: bool,
) -> tuple[int, int]:
    """Print string output.

    Parameters
    ----------
    lint_errors
        a dictionary containing pairs of type {filename: list of errors}
    lint_warnings
        a dictionary containing pairs of type {filename: list of warnings}
    verbose
        When True, output a string if neither an error nor a warning was passed.

    Returns
    -------
    tuple[int, int]
        A tuple containing the total number of errors and the total number of warnings.
    """

    def print_issues(lint_issues: dict[Path, list[LinterError]], issue_type: str) -> None:
        CONSOLE.rule(f"[bold red]JINJA2 LINT {issue_type}")
        for key, issues in lint_issues.items():
            if not issues:
                continue
            tree = Tree(f"{key}")

            for j2_issue in issues:
                tree.add(j2_issue.to_rich(verbose=verbose))
            CONSOLE.print(tree)

    total_lint_errors = sum(len(issues) for issues in lint_errors.values())
    total_lint_warnings = sum(len(issues) for issues in lint_warnings.values())

    if total_lint_errors:
        print_issues(lint_errors, "ERRORS")
    if total_lint_warnings:
        print_issues(lint_warnings, "WARNINGS")

    if not total_lint_errors and not total_lint_warnings:
        if verbose:
            CONSOLE.print("Linting complete. No problems found!", style="green")
    else:
        CONSOLE.print(f"\nJinja2 linting finished with {total_lint_errors} error(s) and {total_lint_warnings} warning(s)")

    return total_lint_errors, total_lint_warnings


def remove_temporary_file(stdin_filename: Path) -> None:
    """Remove temporary file.

    Parameters
    ----------
    stdin_filename
        The name of the temporary file to be removed.
    """
    if stdin_filename:
        stdin_filename.unlink()


def print_string_rules(collection: RulesCollection) -> None:
    """Print active rules as string.

    Parameters
    ----------
    collection
        The RulesCollection to print.
    """
    CONSOLE.rule("[bold red]Rules in the Collection")
    CONSOLE.print(collection.to_rich())


def print_json_rules(collection: RulesCollection) -> None:
    """Print active rules as json.

    Parameters
    ----------
    collection
        The RulesCollection to print as JSON.
    """
    CONSOLE.print_json(collection.to_json())


def run(args: list[str] | None = None) -> int:
    """Run jinja2 linter.

    Parameters
    ----------
    args
        Command line arguments. Defaults to None.

    Returns
    -------
    int
        0 on success
    """
    # ruff: noqa: PLR0912,C901
    # given the number of input parameters, it is acceptable to keep these many branches.

    parser = create_parser()
    options = parser.parse_args(args if args is not None else sys.argv[1:])

    # Enable logs

    if not options.log and not options.stdout:
        logging.disable(sys.maxsize)

    else:
        log_level = logging.DEBUG if options.debug else logging.INFO
        if options.log:
            add_handler(logger, log_level, stream_handler=False)
        if options.stdout:
            add_handler(logger, log_level, stream_handler=True)

    logger.debug("Lint options selected %s", options)

    stdin_filename = None
    file_or_dir_names: list[Path] = [Path(pathname) for pathname in set(options.files)]
    checked_files: list[Path] = []

    if options.stdin and not sys.stdin.isatty():
        with tempfile.NamedTemporaryFile("w", suffix=".j2", delete=False) as stdin_tmpfile:
            stdin_tmpfile.write(sys.stdin.read())
            stdin_filename = Path(stdin_tmpfile.name)
            file_or_dir_names.append(stdin_filename)

    # Collect the rules from the configuration
    collection = RulesCollection(verbose=options.verbose)
    for rules_dir in options.rules_dir:
        collection.extend(RulesCollection.create_from_directory(rules_dir, options.ignore, options.warn).rules)

    # List lint rules
    if options.list:
        if options.json:
            print_json_rules(collection)
        else:
            print_string_rules(collection)
        return 0

    # Version of j2lint
    if options.version:
        CONSOLE.print(f"Jinja2-Linter Version [bold red]{VERSION}")
        return 0

    # Print help message
    if not file_or_dir_names:
        parser.print_help(file=sys.stderr)
        return 1

    files = get_files(file_or_dir_names, options.extensions)

    lint_errors, lint_warnings = get_linting_issues(files, collection, checked_files)

    if options.json:
        logger.debug("JSON output enabled")
        total_lint_errors, _ = print_json_output(lint_errors, lint_warnings)
    else:
        total_lint_errors, _ = print_string_output(lint_errors, lint_warnings, verbose=options.verbose)

    # Remove temporary file
    if stdin_filename is not None:
        remove_temporary_file(stdin_filename)

    return 2 if total_lint_errors else 0

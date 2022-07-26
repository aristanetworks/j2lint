"""cli.py - Command line argument parser.
"""
import sys
import os
import argparse
import logging
import tempfile
import json
from j2lint import NAME, VERSION, DESCRIPTION
from j2lint.linter.collection import RulesCollection
from j2lint.linter.runner import Runner
from j2lint.utils import get_files
from j2lint.logger import logger, add_handler

RULES_DIR = os.path.dirname(os.path.realpath(__file__)) + "/rules"
IGNORE_RULES = WARN_RULES = ['jinja-syntax-error',
                             'single-space-decorator',
                             'operator-enclosed-by-spaces',
                             'jinja-statements-single-space',
                             'jinja-statements-indentation',
                             'jinja-statements-no-tabs',
                             'single-statement-per-line',
                             'jinja-statements-delimiter',
                             'jinja-variable-lower-case',
                             'jinja-variable-format',
                             'S0', 'S1', 'S2', 'S3', 'S4',
                             'S5', 'S6', 'S7', 'V1', 'V2'
                             ]


def create_parser():
    """Initializes a new argument parser object

    Returns:
        Object: Argument parser object
    """
    parser = argparse.ArgumentParser(prog=NAME, description=DESCRIPTION)

    parser.add_argument(dest='files', metavar='FILE', nargs='*', default=[],
                        help='files or directories to lint')
    parser.add_argument('-i', '--ignore', nargs='*',
                        choices=IGNORE_RULES, default=[], help='rules to ignore')
    parser.add_argument('-w', '--warn', nargs='*',
                        choices=WARN_RULES, default=[], help='rules to warn')
    parser.add_argument('-l', '--list', default=False,
                        action='store_true', help='list of lint rules')
    parser.add_argument('-r', '--rules_dir', dest='rules_dir', action='append',
                        default=[RULES_DIR], help='rules directory')
    parser.add_argument('-v', '--verbose', default=False,
                        action='store_true', help='verbose output for lint issues')
    parser.add_argument('-d', '--debug', default=False,
                        action='store_true', help='enable debug logs')
    parser.add_argument('-j', '--json', default=False,
                        action='store_true', help='enable JSON output')
    parser.add_argument('-s', '--stdin', default=False,
                        action='store_true', help='accept template from STDIN')
    parser.add_argument('--log', default=False,
                        action='store_true', help='enable logging')
    parser.add_argument('--version', default=False,
                        action='store_true', help='Version of j2lint')
    parser.add_argument('-o', '--stdout', default=False,
                        action='store_true', help='stdout logging')

    return parser


def sort_issues(issues):
    """Sorted list of issues

    Args:
        issues (list): list of issue dictionaries

    Returns:
        list: list of sorted issue dictionaries
    """
    issues.sort(
        key=lambda issue: (
            issue.filename,
            issue.line_number,
            issue.rule.id
        )
    )
    return issues


def get_linting_issues(file_or_dir_names, collection, checked_files):
    """ checking errors and warnings """
    lint_errors = {}
    lint_warnings = {}
    files = get_files(file_or_dir_names)

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


def print_json_output(lint_errors, lint_warnings):
    """ printing json output """
    json_output = {'ERRORS': [], 'WARNINGS': []}
    for _, errors in lint_errors.items():
        for error in errors:
            json_output['ERRORS'].append(json.loads(str(error.to_json())))
    for _, warnings in lint_warnings.items():
        for warning in warnings:
            json_output['WARNINGS'].append(json.loads(str(warning.to_json())))
    print(f"\n{json.dumps(json_output)}")

    return len(json_output['ERRORS']), len(json_output['WARNINGS'])


def print_string_output(lint_errors, lint_warnings, verbose):
    """ print non-json output """

    def print_issues(lint_issues, issue_type):
        print(f"\nJINJA2 LINT {issue_type}")
        for key, issues in lint_issues.items():
            if not issues:
                continue
            print(f"************ File {key}")
            for j2_issue in issues:
                print(f"{j2_issue.to_string(verbose)}")

    total_lint_errors = sum(len(issues) for _, issues in lint_errors.items())
    total_lint_warnings = sum(len(issues)
                              for _, issues in lint_warnings.items())

    if total_lint_errors:
        print_issues(lint_errors, "ERRORS")
    if total_lint_warnings:
        print_issues(lint_warnings, "WARNINGS")

    if not total_lint_errors and not total_lint_warnings:
        print("\nLinting complete. No problems found.")
    else:
        print(f"\nJinja2 linting finished with "
              f"{total_lint_errors} error(s) and {total_lint_warnings} warning(s)")

    return total_lint_errors, total_lint_warnings


def remove_temporary_file(stdin_filename):
    """ Remove temporary file """
    if stdin_filename:
        os.unlink(stdin_filename)


def run(args=None):
    """Runs jinja2 linter

    Args:
        args ([string], optional): Command line arguments. Defaults to None.

    Returns:
        int: 0 on success
    """
    # pylint: disable=too-many-branches
    # given the number of input parameters, it is acceptable to keep these many branches.

    parser = create_parser()
    options = parser.parse_args(args if args is not None else sys.argv[1:])

    # Enable logs

    if not options.log and not options.stdout:
        logging.disable(sys.maxsize)

    else:
        log_level = logging.INFO
        if options.debug:
            log_level = logging.DEBUG
        if options.log:
            add_handler(logger, False, log_level)
        if options.stdout:
            add_handler(logger, True, log_level)

    logger.debug("Lint options selected %s", options)

    stdin_filename = None
    file_or_dir_names = set(options.files)
    checked_files = set()

    if options.stdin and not sys.stdin.isatty():
        with tempfile.NamedTemporaryFile('w', suffix='.j2', delete=False) as stdin_tmpfile:
            stdin_tmpfile.write(sys.stdin.read())
            stdin_filename = stdin_tmpfile.name
            file_or_dir_names.add(stdin_filename)

    # Collect the rules from the configuration
    collection = RulesCollection(options.verbose)
    for rules_dir in options.rules_dir:
        collection.extend(RulesCollection.create_from_directory(
            rules_dir, options.ignore, options.warn))

    # List lint rules
    if options.list:
        rules = f"Jinja2 lint rules\n{collection}\n"
        print(rules)
        logger.debug(rules)
        return 0

    # Version of j2lint
    if options.version:
        print(f"Jinja2-Linter Version {VERSION}")
        return 0

    # Print help message
    if not file_or_dir_names:
        parser.print_help(file=sys.stderr)
        return 1

    lint_errors, lint_warnings = (
        get_linting_issues(file_or_dir_names, collection, checked_files))

    if options.json:
        logger.debug("JSON output enabled")
        total_lint_errors, _ = print_json_output(lint_errors, lint_warnings)
    else:
        total_lint_errors, _ = print_string_output(lint_errors,
                                                   lint_warnings, options.verbose)

    # Remove temporary file
    remove_temporary_file(stdin_filename)

    if total_lint_errors:
        return 2

    return 0

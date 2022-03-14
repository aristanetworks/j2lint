"""cli.py - Command line argument parser.
"""
import sys
import warnings
import errno
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
from j2lint.settings import settings

RULES_DIR = os.path.dirname(os.path.realpath(__file__)) + "/rules"
IGNORE_RULES = WARN_RULES = ['jinja-syntax-error',
                'single-space-decorator',
                'operator-enclosed-by-spaces',
                'jinja-statements-single-space',
                'jinja-statements-indentation',
                'jinja-statements-no-tabs',
                'single-statement-per-line',
                'jinja-statements-delimeter',
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
    parser.add_argument('-ver', '--version', default=False,
                        action='store_true', help='Version of j2lint')
    parser.add_argument('-stdout', '--vv', default=False,
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
            issue.linenumber,
            issue.rule.id
        )
    )
    return issues


def run(args=None):
    """Runs jinja2 linter

    Args:
        args ([string], optional): Command line arguments. Defaults to None.

    Returns:
        int: 0 on success
    """
    parser = create_parser()
    options = parser.parse_args(args if args is not None else sys.argv[1:])

    # Enable logs

    if not options.log and not options.vv:
        logging.disable(sys.maxsize)

    else:
        log_level = logging.INFO
        if options.debug:
            log_level = logging.DEBUG
        if options.log:
            add_handler(logger, False, log_level)
        if options.vv:
            add_handler(logger, True, log_level)

    logger.debug("Lint options selected {}".format(options))

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
    for rulesdir in options.rules_dir:
        collection.extend(RulesCollection.create_from_directory(
            rulesdir, options.ignore, options.warn))

    # List lint rules
    if options.list:
        rules = "Jinja2 lint rules\n{}\n".format(collection)
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

    # Print verbose output for linting
    if options.verbose:
        settings.verbose = True
        logger.debug("Verbose mode enabled")

    if options.json:
        settings.output = "json"
        logger.debug("JSON output enabled")

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
        lint_errors[file_name].extend(j2_errors)
        lint_warnings[file_name].extend(j2_warnings)

    # Remove temporary file
    if stdin_filename:
        os.unlink(stdin_filename)

    # Sort and print linting issues
    found_errors = False
    found_warnings = False
    total_errors = 0
    total_warnings = 0
    json_output = {}
    if lint_errors:
        for key, errors in lint_errors.items():
            if len(errors):
                total_errors = len(errors)
                if not found_errors:
                    found_errors = True
                    if not options.json:
                        print("\nJINJA2 LINT ERRORS")
                sorted_errors = sort_issues(errors)
                if options.json:
                    json_output['ERRORS'] = ([json.loads(str(error)) for error in sorted_errors])
                else:
                    print("************ File {}".format(key))
                    for j2_error in sorted_errors:
                        print("{}".format(j2_error))
    if lint_warnings:
        for key, warning in lint_warnings.items():
            if len(warning):
                total_warnings = len(warning)
                if not found_warnings:
                    found_warnings = True
                    if not options.json:
                        print("\nJINJA2 LINT WARNINGS")
                sorted_warnings = sort_issues(warning)
                if options.json:
                    json_output['WARNINGS'] = [json.loads(str(warning)) for warning in sorted_warnings]
                else:
                    print("************ File {}".format(key))
                    for j2_warning in sorted_warnings:
                        print("{}".format(j2_warning))
    if options.json:
        print(json.dumps(json_output))
    elif not found_errors and not found_warnings:
        print("Linting complete. No problems found.")
    else:
        print("Jinja2 linting finished with {} issue(s) and {} warning(s)".format(total_errors, total_warnings))

    if found_errors:
        return 2
    return 0

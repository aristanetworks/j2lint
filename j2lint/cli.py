"""cli.py - Command line argument parser.
"""
import sys
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
from j2lint.logger import logger
from j2lint.settings import settings

RULES_DIR = os.path.dirname(os.path.realpath(__file__)) + "/rules"
IGNORE_RULES = ['jinja-syntax-error',
                'single-space-decorator',
                'filter-enclosed-by-spaces',
                'jinja-statement-single-space',
                'jinja-statements-indentation',
                'no-tabs',
                'single-statement-per-line',
                'jinja-delimeter',
                'jinja-variable-lower-case',
                'jinja-variable-format']


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

    # Enable debug logs
    if options.debug:
        logger.setLevel(logging.DEBUG)

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
            rulesdir, options.ignore))

    # List lint rules
    if options.list:
        rules = "Jinja2 lint rules\n{}\n".format(collection)
        print(rules)
        logger.debug(rules)
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

    lint_issues = {}
    files = get_files(file_or_dir_names)

    # Get linting issues
    for file_name in files:
        runner = Runner(collection, file_name, checked_files)
        if file_name not in lint_issues:
            lint_issues[file_name] = []
        lint_issues[file_name].extend(runner.run())

    # Remove temporary file
    if stdin_filename:
        os.unlink(stdin_filename)

    # Sort and print linting issues
    found_issues = False
    json_output = []
    if lint_issues:
        for key, issues in lint_issues.items():
            if len(issues):
                if not found_issues:
                    found_issues = True
                    if not options.json:
                        print("Jinja2 linting issues found")
                sorted_issues = sort_issues(issues)
                if options.json:
                    json_output.extend([json.loads(str(issue))
                                       for issue in sorted_issues])
                else:
                    print("************ File {}".format(key))
                    for issue in sorted_issues:
                        print(issue)
    if options.json:
        print(json.dumps(json_output))
    elif not found_issues:
        print("Linting complete. No problems found.")

    if found_issues:
        return 2
    return 0

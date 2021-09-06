import sys
import errno
import os
import argparse

from j2lint import NAME, VERSION, DESCRIPTION
from j2lint.linter.collection import RulesCollection
from j2lint.linter.runner import Runner
from j2lint.utils import get_jinja_files
from j2lint.logger import logger
from j2lint.settings import settings

RULES_DIR = os.path.dirname(os.path.realpath(__file__)) + "/rules"
IGNORE_RULES = ['indent']


def init_argument_parser():
    """Returns a new initialized argument parser."""
    parser = argparse.ArgumentParser(prog=NAME, description=DESCRIPTION)

    parser.add_argument(dest='files', metavar='FILE', nargs='*', default=[],
                        help='files or directories to lint')
    parser.add_argument('-i', '--ignore', nargs='*',
                        choices=IGNORE_RULES, help='rules to ignore')
    parser.add_argument('-l', '--list', default=False,
                        action='store_true', help='list of lint rules')
    parser.add_argument('-r', '--rules_dir', dest='rules_dir', action='append',
                        default=[RULES_DIR], help='rules directory')
    parser.add_argument('-v', '--verbose', default=False,
                        action='store_true', help='verbose mode')
    return parser


def sort_issues(issues):
    """Returns the sorted list of issues."""
    issues.sort(
        key=lambda issue: (
            issue.filename,
            issue.linenumber,
            issue.rule.id
        )
    )
    return issues


def run(args=None):
    """Run the linter and return the exit code"""
    parser = init_argument_parser()
    options = parser.parse_args(args if args is not None else sys.argv[1:])

    file_or_dir_names = set(options.files)
    checked_files = set()

    # Show a help message
    if not file_or_dir_names:
        parser.print_help(file=sys.stderr)
        return 1

    # Collect the rules from the configuration
    collection = RulesCollection(options.verbose)
    for rulesdir in options.rules_dir:
        collection.extend(RulesCollection.create_from_directory(rulesdir))

    # List rules
    if options.list:
        print("Jinja2 lint rules\n{}\n".format(collection))

    if options.verbose:
        settings.verbose = True

    lint_issues = []
    files = get_jinja_files(file_or_dir_names)

    # Get linting issues
    for file_name in files:
        runner = Runner(collection, file_name, checked_files)
        lint_issues.extend(runner.run())

    # Sort and print linting issues
    if lint_issues:
        print("Jinja2 linting issues found:")
        sorted_issues = sort_issues(lint_issues)
        for issue in sorted_issues:
            print(issue)
        return 2

    print("Linting complete. No problems found.")
    return 0

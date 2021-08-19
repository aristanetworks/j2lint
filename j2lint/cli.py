import sys
import errno
import os
import argparse

from j2lint import NAME, VERSION, DESCRIPTION
from j2lint.linter.collection import RulesCollection
from j2lint.linter.runner import Runner

RULES_DIR = os.path.dirname(os.path.realpath(__file__)) + "/rules"


def init_argument_parser():
    """Returns a new initialized argument parser."""
    parser = argparse.ArgumentParser(prog=NAME, description=DESCRIPTION)

    parser.add_argument(dest='files', metavar='FILE', nargs='*', default=[],
                        help='one or more files or paths')
    parser.add_argument('--rules', dest='rules_dir',
                        default=RULES_DIR, help='Rules directory')
    return parser


def sort_issues(issues):
    """Returns the sorted list of problems."""
    issues.sort(
        key=lambda issue: (
            issue.filename,
            issue.linenumber,
            issue.rule.id
        )
    )
    return issues


def run(args=None):
    """Run the linter and return the exit code."""
    parser = init_argument_parser()
    options = parser.parse_args(args if args is not None else sys.argv[1:])

    file_names = set(options.files)
    checked_files = set()

    # Show a help message on the screen
    if not file_names:
        parser.print_help(file=sys.stderr)
        return 1

    # Collect the rules from the configuration
    collection = RulesCollection()
    for rulesdir in [options.rules_dir]:
        collection.extend(RulesCollection.create_from_directory(rulesdir))

    lint_issues = []
    for file_name in file_names:
        runner = Runner(collection, file_name, checked_files)
        lint_issues.extend(runner.run())

    if lint_issues:
        sorted_issues = sort_issues(lint_issues)
        for issue in sorted_issues:
            print(issue)
        return 2
    print("Linting complete. No problems found.")
    return 0

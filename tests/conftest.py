"""
content of conftest.py
"""
import pathlib

import pytest
from j2lint.cli import create_parser
from j2lint.linter.rule import Rule
from j2lint.linter.error import LinterError
from j2lint.linter.collection import RulesCollection
from j2lint.linter.runner import Runner

CONTENT = "content"

# TODO - proper way to compare LinterError following:
# https://docs.pytest.org/en/7.1.x/how-to/assert.html#defining-your-own-explanation-for-failed-assertions


DEFAULT_RULE_DIR = pathlib.Path(__file__).parent.parent / "j2lint/rules"

@pytest.fixture
def collection():
    return RulesCollection.create_from_directory(DEFAULT_RULE_DIR, [], [])

@pytest.fixture
def make_rules():
    """
    Return a Rule factory that takes one argument
    `count` and returns count rules following the pattern
    where `i` is the index

        id = Ti
        description = test rule i
        short_description = test-rule-i
        severity in [LOW, MEDIUM, HIGH] based on i % 3

    The factory can then be invoked as follow:

        def test_blah(makes_rules):
            rules = make_rules(5)
            # do stuff with rules
    """

    def __make_n_rules(count):
        def get_severity(integer: int):
            return (
                "LOW"
                if integer % 3 == 0
                else ("MEDIUM" if integer % 3 == 1 else "HIGH")
            )

        rules = []
        for i in range(count):
            r_obj = Rule()
            r_obj.id = f"T{i}"
            r_obj.description = f"test rule {i}"
            r_obj.short_description = f"test-rule-{i}"
            r_obj.severity = get_severity(i)
            rules.append(r_obj)
        return rules

    return __make_n_rules


@pytest.fixture
def test_rule(make_rules):
    """
    return a Rule object to use in test
    from the make_rules - it will have

        id = T0
        description = test rule 0
        short_description = test-rule-0
        severity = LOW
    """
    yield make_rules(1)[0]


@pytest.fixture
def test_other_rule(make_rules):
    """
    return the second  Rule object to use in test
    from the make_rules - it will have

        id = T1
        description = test rule 1
        short_description = test-rule-1
        severity = MEDIUM
    """
    yield make_rules(2)[1]


@pytest.fixture
def make_issues(make_rules):
    """
    Returns a factory that generates `count` issues and
    return them as a list

    The fixture invokes `make_rules` first with count
    and every LinterError generated is using the rule
    of same index.

    The line number is index + 1 so issue 0 will have
    line number 1

    the line content is always "dummy" and the filename
    "dummy.j2"

    The factory can then be invoked as follow:

        def test_blah(makes_issues):
            issues = make_issues(5)
            # do stuff with issues
    """

    def __make_n_issues(count):
        issues = []
        rules = make_rules(count)
        for i in range(0, count):
            issues.append(LinterError(i + 1, "dummy", "dummy.j2", rules[i]))
        return issues

    return __make_n_issues


@pytest.fixture
def make_issue_from_rule():
    """
    Returns a factory that generates an issue based on
    a Rule object

    it uses line 42, the line content is "dummy" and the
    filename is "dummy.j2"
    """

    def __make_issue_from_rule(rule):
        yield LinterError(42, "dummy", "dummy.j2", rule)

    return __make_issue_from_rule


@pytest.fixture
def test_issue(make_issues):
    """
    Get the first issue from the make_issues factory

    Note: it will use rule T0 as per design
    """
    yield make_issues(1)[0]


@pytest.fixture
def test_collection(test_rule):
    """
    test_collection using one rule `test_rule`
    """
    collection = RulesCollection()
    collection.extend([test_rule])
    yield collection


@pytest.fixture
def test_runner(test_collection):
    """
    Fixture to get a test runner using the test_collection
    """
    yield Runner(test_collection, "test.j2", checked_files=None)


@pytest.fixture
def j2lint_usage_string():
    """
    Fixture to get the help generated by argparse
    """
    yield create_parser().format_help()


@pytest.fixture()
def template_tmp_dir(tmp_path_factory):
    """
    Create a tmp directory with multiple files and hidden files
    """
    rules = tmp_path_factory.mktemp("rules", numbered=False)
    rules_subdir = rules / "rules_subdir"
    rules_subdir.mkdir()
    # no clue if we are suppose to find these
    rules_hidden_subdir = rules / ".rules_hidden_subdir"
    rules_hidden_subdir.mkdir()

    # in each directory add one matching file and one none matching
    rules_j2 = rules / "rules.j2"
    rules_j2.write_text(CONTENT)
    rules_txt = rules / "rules.txt"
    rules_txt.write_text(CONTENT)

    rules_subdir_j2 = rules_subdir / "rules.j2"
    rules_subdir_j2.write_text(CONTENT)
    rules_subdir_txt = rules_subdir / "rules.txt"
    rules_subdir_txt.write_text(CONTENT)

    rules_hidden_subdir_j2 = rules_hidden_subdir / "rules.j2"
    rules_hidden_subdir_j2.write_text(CONTENT)
    rules_hidden_subdir_txt = rules_hidden_subdir / "rules.txt"
    rules_hidden_subdir_txt.write_text(CONTENT)

    yield [str(rules)]

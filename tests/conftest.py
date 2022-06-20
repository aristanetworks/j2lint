"""
content of conftest.py
"""
from unittest.mock import create_autospec
import pytest
from j2lint.settings import settings
from j2lint.cli import create_parser
from j2lint.linter.rule import Rule
from j2lint.linter.error import LinterError
from j2lint.linter.collection import RulesCollection

CONTENT = "content"

# TODO - proper way to compare LinterError following:
# https://docs.pytest.org/en/7.1.x/how-to/assert.html#defining-your-own-explanation-for-failed-assertions


@pytest.fixture(autouse=True)
def default_settings():
    """
    Make sure all tests start with default settings
    """
    settings.verbose = False
    settings.log_level = "info"
    settings.output = "text"


@pytest.fixture
def mock_rule():
    """
    Return a MagicMock with the spec of a Rule object
    """
    r_obj = create_autospec(Rule)
    r_obj.id = "T1"
    r_obj.short_description = "pytest-fixture"
    r_obj.description = "Pytest Fixture Rule"
    r_obj.severity = "LOW"
    yield r_obj


@pytest.fixture
def mock_collection(mock_rule):
    """
    Return a MagicMock with the spec of a Collection object
    """
    collection = create_autospec(RulesCollection)
    # one rule for now
    collection.rules = [mock_rule]
    yield collection


@pytest.fixture
def test_rule():
    """
    return a Rule object to use in tests
    """
    r_obj = Rule()
    r_obj.id = "T0"
    r_obj.description = "test Rule object"
    r_obj.short_description = "test-rule"
    r_obj.severity = "LOW"
    yield r_obj


@pytest.fixture
def test_other_rule():
    """
    return a Rule object to use in tests
    """
    r_obj = Rule()
    r_obj.id = "T1"
    r_obj.description = "other test Rule object"
    r_obj.short_description = "other-test-rule"
    r_obj.severity = "HIGH"
    yield r_obj


@pytest.fixture
def test_collection(test_rule):
    collection = RulesCollection()
    collection.extend([test_rule])
    yield collection


@pytest.fixture
def make_rules():
    """
    Return a Rule factory that takes one argument
    `count`
    """

    def __make_n_rules(count):
        def get_severity(integer: int):
            return (
                "LOW"
                if integer % 3 == 0
                else ("MEDIUM" if integer % 3 == 1 else "HIGH")
            )

        rules = []
        for i in range(0, count):
            r_obj = Rule()
            r_obj.id = f"T{i}"
            r_obj.description = f"test rule {i}"
            r_obj.short_description = f"test-rule-{i}"
            r_obj.severity = get_severity(i)
            rules.append(r_obj)
        return rules

    return __make_n_rules


@pytest.fixture
def make_issues(make_rules):
    """
    Returns a factory that generates `count` issues
    of type `issue_type`. Every alternate issue use one
    of the two fixtures rules
    """

    def __make_n_issues(count, issue_type):
        issues = {issue_type: []}
        rules = make_rules(count)
        for i in range(0, count):
            issues[issue_type].append(LinterError(i + 1, "dummy", "dummy.j2", rules[i]))
        return issues

    return __make_n_issues


@pytest.fixture
def j2lint_usage_string():
    return create_parser().format_help()


@pytest.fixture()
def template_tmp_dir(tmp_path_factory):
    """
    Create a tmp directory for test purposes
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

"""
content of conftest.py
"""
from unittest.mock import create_autospec
import pytest
from j2lint.linter.rule import Rule
from j2lint.linter.collection import RulesCollection

CONTENT = "content"


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
    yield r_obj


@pytest.fixture
def test_collection(test_rule):
    collection = RulesCollection()
    collection.extend([test_rule])
    yield collection


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

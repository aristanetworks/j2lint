"""
content of conftest.py
"""
from unittest.mock import create_autospec
import pytest
from j2lint.linter.rule import Rule

CONTENT = "content"


@pytest.fixture
def rule():
    """
    Return a MagicMock with the spec of a Rule object
    """
    r_obj = create_autospec(Rule)
    r_obj.id = "T1"
    r_obj.short_description = "pytest-fixture"
    r_obj.description = "Pytest Fixture Rule"
    r_obj.severity = "LOW"
    return r_obj


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

"""
Tests for j2lint.linter.rule.py
"""
import pytest

from j2lint.linter.rule import Rule


@pytest.fixture
def rule():
    """
    return a Rule object to use in tests
    """
    r_obj = Rule()
    r_obj.id = "S2"
    r_obj.description = "test Rule object"
    return r_obj


class TestRule:
    def test__repr__(self, rule):
        """
        Test the Rule __repr__ format
        """
        assert str(rule) == "S2: test Rule object"

    @pytest.mark.skip("This method will be removed")
    def test_is_valid_language(self, rule, file):
        """ """

    @pytest.mark.skip("This method is overwritten  by child classes")
    def test_checklines(self):
        """ """

    @pytest.mark.skip("This method is overwritten by child classes")
    def test_checkfulltexts(self):
        """ """

"""
Tests for j2lint.linter.rule.py
"""
import pytest

from j2lint.linter.rule import Rule


class TestRule:
    def test__repr__(self, test_rule):
        """
        Test the Rule __repr__ format
        """
        assert str(test_rule) == "T0: test Rule object"

    @pytest.mark.skip("This method will be removed")
    def test_is_valid_language(self, test_rule, file):
        """ """

    @pytest.mark.skip("This method is overwritten  by child classes")
    def test_checklines(self):
        """ """

    @pytest.mark.skip("This method is overwritten by child classes")
    def test_checkfulltexts(self):
        """ """

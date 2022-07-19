"""
Tests for j2lint.settings.py
"""
from j2lint.settings import settings


def test_default_settings():
    """
    NOTE: the Settings class should probably be removed from a design point of view

    This test is only here to have the structure
    """
    assert settings.verbose is False
    assert settings.log_level == "info"
    assert settings.output == "text"

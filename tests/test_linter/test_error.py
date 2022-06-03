"""
Tests for j2lint.linter.error.py
"""
import pytest

from j2lint.settings import settings
from j2lint.linter.error import LinterError

RULE_TEXT_OUTPUT = (
    "Linting rule: T1\n"
    "Rule description: Pytest Fixture Rule\n"
    "Error line: fake filename:42 fake line\n"
    "Error message: Pytest Fixture Rule\n"
)
RULE_JSON_OUTPUT = (
    '{"id": "T1", "message": "Pytest Fixture Rule", '
    '"filename": "fake filename", "linenumber": 42, '
    '"line": "fake line", "severity": "LOW"}'
)


@pytest.fixture
def linter_error(rule, message=None):
    return LinterError(42, "fake line", "fake filename", rule, message=message)


@pytest.mark.parametrize(
    "verbose, output, expected",
    [
        (False, "text", "fake filename:42 Pytest Fixture Rule (pytest-fixture)"),
        (False, "json", RULE_JSON_OUTPUT),
        (
            True,
            "text",
            RULE_TEXT_OUTPUT,
        ),
        (True, "json", RULE_JSON_OUTPUT),
        (True, "blah", RULE_TEXT_OUTPUT),
    ],
)
def test_LinterError_repr(linter_error, verbose, output, expected):
    """
    Test the different __repr__ formats for LinterError

    Note: this implementation is probably not the best as it relies on
          external settings being set and __repr__ should not really
          return multiple formats.
          It would be clean to make different function rather than
          abusing __repr__ this way
    TODO: refactor
    """
    settings.verbose = verbose
    settings.output = output
    assert repr(linter_error) == expected

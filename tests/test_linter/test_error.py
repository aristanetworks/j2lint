"""
Tests for j2lint.linter.error.py
"""
import pytest

RULE_TEXT_OUTPUT = (
    "Linting rule: T0\n"
    "Rule description: test rule 0\n"
    "Error line: dummy.j2:1 dummy\n"
    "Error message: test rule 0\n"
)
RULE_JSON_OUTPUT = (
    '{"id": "T0", "message": "test rule 0", '
    '"filename": "dummy.j2", "line_number": 1, '
    '"line": "dummy", "severity": "LOW"}'
)


# @pytest.mark.parametrize(
#     "verbose, output, expected",
#     [
#         (False, "text", "dummy.j2:1 test rule 0 (test-rule-0)"),
#         (False, "json", RULE_JSON_OUTPUT),
#         (
#             True,
#             "text",
#             RULE_TEXT_OUTPUT,
#         ),
#         (True, "json", RULE_JSON_OUTPUT),
#         (True, "blah", RULE_TEXT_OUTPUT),
#     ],
# )
# def test_LinterError_repr(test_issue, verbose, output, expected):
#     """
#     Test the different __repr__ formats for LinterError
#
#     Note: this implementation is probably not the best as it relies on
#           external settings being set and __repr__ should not really
#           return multiple formats.
#           It would be clean to make different function rather than
#           abusing __repr__ this way
#     TODO: refactor
#     """
#     settings.verbose = verbose
#     settings.output = output
#     assert repr(test_issue) == expected

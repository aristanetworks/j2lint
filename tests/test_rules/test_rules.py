import logging

import pytest

from j2lint.linter.collection import RulesCollection


@pytest.fixture
def collection():
    return RulesCollection.create_from_directory("j2lint/rules", [], [])


PARAMS = [
    (
        "tests/test_rules/data/JinjaTemplateSyntaxErrorRule.j2",
        [("S0", 1)],
        [],
        [],
    ),
    (
        "tests/test_rules/data/JinjaVariableHasSpaceRule.j2",
        [("S1", 1), ("S1", 2), ("S1", 3)],
        [],
        [],
    ),
    (
        "tests/test_rules/data/JinjaOperatorHasSpaceRule.j2",
        [("S2", 1), ("S2", 2), ("S2", 3), ("S2", 6), ("S2", 8), ("S2", 10)],
        [],
        [],
    ),
    (
        "tests/test_rules/data/JinjaTemplateIndentationRule.j2",
        [("S3", 2), ("S3", 6), ("S3", 5)],
        [],
        [],
    ),
    (
        "tests/test_rules/data/JinjaTemplateIndentationRule_fail.j2",
        [("S0", 2), ("S3", 2)],
        [],
        [
            (
                "root",
                logging.ERROR,
                "Indentation check failed for file tests/test_rules/data/JinjaTemplateIndentationRule_fail.j2: Error: Tag is out of order 'endfor'",
            )
        ],
    ),
    (
        "tests/test_rules/data/JinjaStatementHasSpacesRule.j2",
        [("S4", 1), ("S4", 2), ("S4", 3)],
        [],
        [],
    ),
    (
        "tests/test_rules/data/JinjaTemplateNoTabsRule.j2",
        [("S5", 1)],
        [],
        [],
    ),
    (
        "tests/test_rules/data/JinjaStatementDelimiterRule.j2",
        [("S6", 1), ("S6", 3), ("S6", 5)],
        [],
        [],
    ),
    (
        "tests/test_rules/data/JinjaTemplateSingleStatementRule.j2",
        [("S7", 1)],
        [],
        [],
    ),
    (
        "tests/test_rules/data/JinjaVariableNameCaseRule.j2",
        [("V1", 1), ("V1", 2), ("V1", 3)],
        [],
        [],
    ),
    (
        "tests/test_rules/data/JinjaVariableNameFormatRule.j2",
        [("V2", 1)],
        [],
        [],
    ),
]

LOGGER = logging.getLogger("")
LOGGER.setLevel(logging.INFO)


@pytest.mark.parametrize(
    "filename, j2_errors_ids, j2_warnings_ids, expected_log",
    PARAMS,
)
def test_rules(
    caplog, collection, filename, j2_errors_ids, j2_warnings_ids, expected_log
):

    errors, warnings = collection.run({"path": filename})

    errors_ids = [(error.rule.id, error.linenumber) for error in errors]
    errors_messages = "\n".join([error.rule.description for error in errors])
    LOGGER.info(errors_messages)

    warnings_ids = [(warning.rule.id, warning.linenumber) for warning in warnings]

    assert caplog.record_tuples == expected_log

    assert warnings_ids == j2_warnings_ids
    assert errors_ids == j2_errors_ids

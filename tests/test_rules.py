import logging

import pytest

from j2lint.linter.collection import RulesCollection


@pytest.fixture
def collection():
    return RulesCollection.create_from_directory("j2lint/rules", [], [])


PARAMS = [
    (
        "tests/data/JinjaTemplateSyntaxErrorRule.j2",
        [("S0", 1)],
        [],
    ),
    (
        "tests/data/JinjaVariableHasSpaceRule.j2",
        [("S1", 1), ("S1", 2), ("S1", 3)],
        [],
    ),
    (
        "tests/data/JinjaOperatorHasSpaceRule.j2",
        [("S2", 1), ("S2", 2), ("S2", 3)],
        [],
    ),
    (
        "tests/data/JinjaTemplateIndentationRule.j2",
        [("S3", 2), ("S3", 6), ("S3", 5)],
        [],
    ),
    (
        "tests/data/JinjaStatementHasSpacesRule.j2",
        [("S4", 1), ("S4", 2), ("S4", 3)],
        [],
    ),
    (
        "tests/data/JinjaTemplateNoTabsRule.j2",
        [("S5", 1)],
        [],
    ),
    (
        "tests/data/JinjaStatementDelimeterRule.j2",
        [("S6", 1), ("S6", 3), ("S6", 5)],
        [],
    ),
    (
        "tests/data/JinjaTemplateSingleStatementRule.j2",
        [("S7", 1)],
        [],
    ),
    (
        "tests/data/JinjaVariableNameCaseRule.j2",
        [("V1", 1), ("V1", 2), ("V1", 3)],
        [],
    ),
    (
        "tests/data/JinjaVariableNameFormatRule.j2",
        [("V2", 1)],
        [],
    ),
]

LOGGER = logging.getLogger("")
LOGGER.setLevel(logging.INFO)


@pytest.mark.parametrize(
    "filename, j2_errors_ids, j2_warnings_ids",
    PARAMS,
)
def test_rules(collection, filename, j2_errors_ids, j2_warnings_ids):

    LOGGER.debug(collection.rules)
    errors, warnings = collection.run({"path": filename})

    errors_ids = [(error.rule.id, error.linenumber) for error in errors]
    errors_messages = "\n".join([error.rule.description for error in errors])
    LOGGER.info(errors_messages)

    warnings_ids = [(warning.rule.id, warning.linenumber) for warning in warnings]

    assert warnings_ids == j2_warnings_ids
    assert errors_ids == j2_errors_ids

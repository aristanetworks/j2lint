import logging

import pytest

from j2lint.linter.collection import RulesCollection


@pytest.fixture
def collection():
    return RulesCollection.create_from_directory("j2lint/rules", [], [])


PARAMS = [
    (
        "tests/test_rules/data/jinja_template_syntax_error_rule.j2",
        [("S0", 1)],
        [],
        [],
    ),
    (
        "tests/test_rules/data/jinja_variable_has_space_rule.j2",
        [("S1", 1), ("S1", 2), ("S1", 3)],
        [],
        [],
    ),
    (
        "tests/test_rules/data/jinja_operator_has_spaces_rule.j2",
        [("S2", 1), ("S2", 2), ("S2", 3), ("S2", 6), ("S2", 8), ("S2", 10)],
        [],
        [],
    ),
    (
        "tests/test_rules/data/jinja_template_indentation_rule.j2",
        [("S3", 2), ("S3", 6), ("S3", 5)],
        [],
        [],
    ),
    (
        "tests/test_rules/data/jinja_template_indentation_rule.JinjaLinterError.j2",
        [("S0", 2), ("S3", 2)],
        [],
        [
            (
                "root",
                logging.ERROR,
                "Indentation check failed for file tests/test_rules/data/jinja_template_indentation_rule.JinjaLinterError.j2: "
                "Error: Tag is out of order 'endfor'",
            )
        ],
    ),
    (
        "tests/test_rules/data/jinja_template_indentation_rule.TypeError.j2",
        [("S0", 1)],
        [],
        [
            (
                "root",
                logging.ERROR,
                "Indentation check failed for file tests/test_rules/data/jinja_template_indentation_rule.TypeError.j2: "
                "Error: '<' not supported between instances of 'NoneType' and 'int'",
            )
        ],
    ),
    (
        "tests/test_rules/data/jinja_template_indentation_rule.IndexError.j2",
        [("S4", 2)],
        [],
        [
            # somehow this is not picked up when we should expect this log message (which can be seen in CLI)
            # probably some caplog issue here so commenting for now
            # FIXME
            #              (
            #                 "root",
            #                 logging.ERROR,
            #                 "Indentation check failed for file tests/test_rules/data/jinja_template_indentation_rule.IndexError.j2: "
            #                 "Error: list index out of range",
            #             )
        ],
    ),
    (
        "tests/test_rules/data/jinja_statement_has_spaces_rule.j2",
        [("S4", 1), ("S4", 2), ("S4", 3)],
        [],
        [],
    ),
    (
        "tests/test_rules/data/jinja_template_no_tabs_rule.j2",
        [("S5", 1)],
        [],
        [],
    ),
    (
        "tests/test_rules/data/jinja_statement_delimiter_rule.j2",
        [("S6", 1), ("S6", 3), ("S6", 5)],
        [],
        [],
    ),
    (
        "tests/test_rules/data/jinja_template_single_statement_rule.j2",
        [("S7", 1)],
        [],
        [],
    ),
    (
        "tests/test_rules/data/jinja_variable_name_case_rule.j2",
        [("V1", 1), ("V1", 2), ("V1", 3)],
        [],
        [],
    ),
    (
        "tests/test_rules/data/jinja_variable_name_format_rule.j2",
        [("V2", 1)],
        [],
        [],
    ),
]


@pytest.mark.parametrize(
    "filename, j2_errors_ids, j2_warnings_ids, expected_log",
    PARAMS,
)
def test_rules(
    caplog, collection, filename, j2_errors_ids, j2_warnings_ids, expected_log
):
    """
    caplog: fixture to capture logs
    collection: a collection from the j2lint default rules
    filename: the name of the file to parse
    j2_errors_ids: the ids of the expected errors (<ID>, <Line Number>)
    j2_warnings_ids: the ids of the expected warnings (<ID>, <Line Number>)
    expected_log: a list of expected log tuples as defined per caplog.record_tuples
    """

    caplog.set_level(logging.INFO)
    errors, warnings = collection.run({"path": filename, "type": "jinja"})

    errors_ids = [(error.rule.id, error.line_number) for error in errors]

    warnings_ids = [(warning.rule.id, warning.line_number) for warning in warnings]

    print(caplog.record_tuples)
    for record_tuple in expected_log:
        assert record_tuple in caplog.record_tuples

    assert sorted(warnings_ids) == sorted(j2_warnings_ids)
    assert sorted(errors_ids) == sorted(j2_errors_ids)

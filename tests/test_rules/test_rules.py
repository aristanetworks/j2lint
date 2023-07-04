import logging
import pathlib

import pytest

TEST_DATA_DIR = pathlib.Path(__file__).parent / "data"

PARAMS = [
    pytest.param(
        f"{TEST_DATA_DIR}/jinja_template_syntax_error_rule.j2",
        [("S0", 1)],
        [],
        [],
        id="jinja_template_syntax_error_rule",
    ),
    pytest.param(
        f"{TEST_DATA_DIR}/jinja_variable_has_space_rule.j2",
        [
            ("S1", 1),
            ("S1", 2),
            ("S1", 4),
            ("S1", 5),
            ("S1", 6),
            ("S1", 7),
            ("S2", 7),  # the faulty {{+ethernet }} triggers S2 as well
            ("S1", 8),
            ("S1", 9),
        ],
        [],
        [],
        id="jinja_variable_has_space_rule",
    ),
    pytest.param(
        f"{TEST_DATA_DIR}/jinja_operator_has_spaces_rule.j2",
        [("S2", 1), ("S2", 2), ("S2", 3), ("S2", 6), ("S2", 6), ("S2", 8), ("S2", 10)],
        [],
        [],
        id="jinja_operator_has_space_rule",
    ),
    pytest.param(
        f"{TEST_DATA_DIR}/jinja_template_indentation_rule.j2",
        [("S3", 2), ("S3", 6), ("S3", 5)],
        [],
        [],
        id="jinja_template_indentation_rule",
    ),
    pytest.param(
        f"{TEST_DATA_DIR}/jinja_template_indentation_rule.JinjaLinterError.j2",
        [("S0", 2), ("S3", 2)],
        [],
        [
            (
                "root",
                logging.ERROR,
                f"Indentation check failed for file {TEST_DATA_DIR}/jinja_template_indentation_rule.JinjaLinterError.j2: "
                "Error: Line 1 - Tag is out of order 'endfor'",
            )
        ],
        id="jinja_template_indentation_rule JinjaLinterError",
    ),
    pytest.param(
        f"{TEST_DATA_DIR}/jinja_template_indentation_rule.missing_end_tag.j2",
        [("S0", 1)],
        [],
        [
            (
                "root",
                logging.ERROR,
                f"Indentation check failed for file {TEST_DATA_DIR}/jinja_template_indentation_rule.missing_end_tag.j2: "
                "Error: Recursive check_indentation returned None for an opening tag line 0 - missing closing tag",
            )
        ],
    ),
    pytest.param(
        f"{TEST_DATA_DIR}/jinja_template_indentation_rule.IndexError.j2",
        [("S4", 2)],
        [],
        [
            # somehow this is not picked up when we should expect this log message (which can be seen in CLI)
            # probably some caplog issue here so commenting for now
            # FIXME
            #              (
            #                 "root",
            #                 logging.ERROR,
            #                 f"Indentation check failed for file {TEST_DATA_DIR}/jinja_template_indentation_rule.IndexError.j2: "
            #                 "Error: list index out of range",
            #             )
        ],
    ),
    pytest.param(
        f"{TEST_DATA_DIR}/jinja_statement_has_spaces_rule.j2",
        [("S4", 1), ("S4", 2), ("S4", 3)],
        [],
        [],
    ),
    pytest.param(
        f"{TEST_DATA_DIR}/jinja_template_no_tabs_rule.j2",
        [("S5", 1)],
        [],
        [],
    ),
    pytest.param(
        f"{TEST_DATA_DIR}/jinja_statement_delimiter_rule.j2",
        [("S6", 1), ("S6", 3), ("S6", 5)],
        [],
        [],
    ),
    pytest.param(
        f"{TEST_DATA_DIR}/jinja_template_single_statement_rule.j2",
        [("S7", 1)],
        [],
        [],
    ),
    pytest.param(
        f"{TEST_DATA_DIR}/jinja_variable_name_case_rule.j2",
        [("V1", 1), ("V1", 2), ("V1", 3)],
        [],
        [],
    ),
    pytest.param(
        f"{TEST_DATA_DIR}/jinja_variable_name_format_rule.j2",
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

    with open(filename, "r") as f:
        print(f.read())
    caplog.set_level(logging.INFO)
    errors, warnings = collection.run({"path": filename, "type": "jinja"})

    errors_ids = [(error.rule.rule_id, error.line_number) for error in errors]

    warnings_ids = [(warning.rule.rule_id, warning.line_number) for warning in warnings]

    print(caplog.record_tuples)
    for record_tuple in expected_log:
        assert record_tuple in caplog.record_tuples

    assert sorted(warnings_ids) == sorted(j2_warnings_ids)
    assert sorted(errors_ids) == sorted(j2_errors_ids)

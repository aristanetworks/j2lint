# Copyright (c) 2021-2024 Arista Networks, Inc.
# Use of this source code is governed by the MIT license
# that can be found in the LICENSE file.
import logging
import pathlib

import pytest

TEST_DATA_DIR = pathlib.Path(__file__).parent / "data"

PARAMS = [
    pytest.param(
        f"{TEST_DATA_DIR}/jinja_template_syntax_error_rule.j2",
        [("S0", 6)],
        [],
        [],
        id="jinja_template_syntax_error_rule",
    ),
    pytest.param(
        f"{TEST_DATA_DIR}/jinja_variable_has_space_rule.j2",
        [
            ("S1", 6),
            ("S1", 7),
            ("S1", 9),
            ("S1", 10),
            ("S1", 11),
            ("S1", 12),
            ("S2", 12),  # the faulty {{+ethernet }} triggers S2 as well
            ("S1", 13),
            ("S1", 14),
        ],
        [],
        [],
        id="jinja_variable_has_space_rule",
    ),
    pytest.param(
        f"{TEST_DATA_DIR}/jinja_operator_has_spaces_rule.j2",
        [
            ("S2", 6),
            ("S2", 7),
            ("S2", 8),
            ("S2", 11),
            ("S2", 11),
            ("S2", 13),
            ("S2", 15),
        ],
        [],
        [],
        id="jinja_operator_has_space_rule",
    ),
    pytest.param(
        f"{TEST_DATA_DIR}/jinja_template_indentation_rule.j2",
        [("S3", 7), ("S3", 11), ("S3", 10)],
        [],
        [],
        id="jinja_template_indentation_rule",
    ),
    pytest.param(
        f"{TEST_DATA_DIR}/jinja_template_indentation_rule.JinjaLinterError.j2",
        [("S0", 7), ("S3", 7)],
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
        [("S0", 6)],
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
        [("S4", 7)],
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
        [("S4", 6), ("S4", 7), ("S4", 8)],
        [],
        [],
    ),
    pytest.param(
        f"{TEST_DATA_DIR}/jinja_template_no_tabs_rule.j2",
        [("S5", 6)],
        [],
        [],
    ),
    pytest.param(
        f"{TEST_DATA_DIR}/jinja_statement_delimiter_rule.j2",
        [("S6", 6), ("S6", 8), ("S6", 10)],
        [],
        [],
    ),
    pytest.param(
        f"{TEST_DATA_DIR}/jinja_template_single_statement_rule.j2",
        [("S7", 6)],
        [],
        [],
    ),
    pytest.param(
        f"{TEST_DATA_DIR}/jinja_variable_name_case_rule.j2",
        [("V1", 6), ("V1", 7), ("V1", 8)],
        [],
        [],
    ),
    pytest.param(
        f"{TEST_DATA_DIR}/jinja_variable_name_format_rule.j2",
        [("V2", 6)],
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
    errors, warnings = collection.run(filename)

    errors_ids = [(error.rule.rule_id, error.line_number) for error in errors]

    warnings_ids = [(warning.rule.rule_id, warning.line_number) for warning in warnings]

    print(caplog.record_tuples)
    for record_tuple in expected_log:
        assert record_tuple in caplog.record_tuples

    assert sorted(warnings_ids) == sorted(j2_warnings_ids)
    assert sorted(errors_ids) == sorted(j2_errors_ids)

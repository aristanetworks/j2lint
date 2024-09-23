# Copyright (c) 2021-2024 Arista Networks, Inc.
# Use of this source code is governed by the MIT license
# that can be found in the LICENSE file.
"""
Tests for j2lint.linter.rule.py
"""

import logging
import pathlib

import pytest

TEST_DATA_DIR = pathlib.Path(__file__).parent / "data"


class TestRule:
    def test__repr__(self, test_rule):
        """
        Test the Rule __repr__ format
        """
        assert str(test_rule) == "T0: test rule 0"

    @pytest.mark.skip("This method will be removed and is tested through other methods")
    def test_is_valid_language(self, test_rule, file):
        """ """

    @pytest.mark.parametrize(
        "checktext, checkline, file_path, expected_errors_ids, expected_logs",
        [
            pytest.param(
                None,
                0,
                {"path": f"{TEST_DATA_DIR}/test.j2"},
                [],
                [],
                id="no error",
            ),
            pytest.param(
                None,
                1,
                {"path": f"{TEST_DATA_DIR}/test.j2"},
                [("T0", 42), ("T0", 42), ("T0", 42), ("T0", 42), ("T0", 42)],
                [],
                id="checkline rule error",
            ),
            pytest.param(
                2,
                None,
                {"path": "tests/test_linter/data/test.j2"},
                [("T0", 42), ("T0", 42)],
                [],
                id="checktext rule error",
            ),
        ],
    )
    def test_checkrule(
        self,
        caplog,
        test_rule,
        make_issue_from_rule,
        checktext,
        checkline,
        file_path,
        expected_errors_ids,
        expected_logs,
    ):
        """
        Test the Rule.checkrule method
        """

        def raise_NotImplementedError(*args, **kwargs):
            raise NotImplementedError

        def return_empty_list(*args, **kwargs):
            return []

        caplog.set_level(logging.DEBUG)

        # Build checktext and checkline
        if checktext is None:
            test_rule.checktext = raise_NotImplementedError
        elif checktext == 0:
            test_rule.checktext = return_empty_list
        else:
            # checktext > 0
            test_rule.checktext = lambda x, y: [issue for i in range(checktext) for issue in make_issue_from_rule(test_rule)]

        if checkline is None:
            test_rule.checkline = raise_NotImplementedError

        elif checkline == 0:
            test_rule.checkline = return_empty_list
        else:
            # checkline > 0
            test_rule.checkline = lambda x, y, line_no=0: [issue for i in range(checkline) for issue in make_issue_from_rule(test_rule)]

        with open(file_path["path"], encoding="utf-8") as file_d:
            errors = test_rule.checkrule(file_path, file_d.read())
        print(errors)
        errors_ids = [(error.rule.rule_id, error.line_number) for error in errors]
        assert errors_ids == expected_errors_ids
        assert caplog.record_tuples == expected_logs

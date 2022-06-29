"""
Tests for j2lint.linter.rule.py
"""
import logging
import pytest

from j2lint.linter.rule import logger
from j2lint.linter.rule import Rule


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
        "check, file_path, expected_errors_ids, expected_logs",
        [
            pytest.param(
                True,
                {"path": "tests/test_linter/data/test.txt"},
                [],
                [
                    (
                        "root",
                        logging.DEBUG,
                        "Skipping file {'path': 'tests/test_linter/data/test.txt'}. Linter does not support linting this file type",
                    )
                ],
                id="file is wrong type",
            ),
            pytest.param(
                lambda x: None,
                {"path": "tests/test_linter/data/test.j2"},
                [],
                [],
                id="no error",
            ),
            pytest.param(
                lambda x: True,
                {"path": "tests/test_linter/data/test.j2"},
                [("T0", 1)],
                [],
                id="rule error",
            ),
        ],
    )
    def test_checklines(
        self, caplog, test_rule, check, file_path, expected_errors_ids, expected_logs
    ):
        """
        Test the Rule.checklines method
        """
        caplog.set_level(logging.DEBUG)
        test_rule.check = check
        with open(file_path["path"], "r", encoding="utf-8") as file_d:
            errors = test_rule.checklines(file_path, file_d.read())
        errors_ids = [(error.rule.id, error.line_number) for error in errors]
        assert errors_ids == expected_errors_ids
        assert caplog.record_tuples == expected_logs

    @pytest.mark.parametrize(
        "checktext, file_path, expected_errors_ids, expected_logs",
        [
            pytest.param(
                True,
                {"path": "tests/test_linter/data/test.txt"},
                [],
                [
                    (
                        "root",
                        logging.DEBUG,
                        "Skipping file {'path': 'tests/test_linter/data/test.txt'}. Linter does not support linting this file type",
                    )
                ],
                id="file is wrong type",
            ),
            pytest.param(
                lambda x, y: [],
                {"path": "tests/test_linter/data/test.j2"},
                [],
                [],
                id="no error",
            ),
            pytest.param(
                lambda x, y: [(1, "section1", "message1"), (2, "section2", "message2")],
                {"path": "tests/test_linter/data/test.j2"},
                [("T0", 1), ("T0", 2)],
                [],
                id="rule error",
            ),
        ],
    )
    def test_checkfulltext(
        self,
        caplog,
        test_rule,
        checktext,
        file_path,
        expected_errors_ids,
        expected_logs,
    ):
        """
        Test the Rule.checkfulltext method
        """
        caplog.set_level(logging.DEBUG)
        test_rule.checktext = checktext
        with open(file_path["path"], "r", encoding="utf-8") as file_d:
            errors = test_rule.checkfulltext(file_path, file_d.read())
        errors_ids = [(error.rule.id, error.line_number) for error in errors]
        assert errors_ids == expected_errors_ids
        assert caplog.record_tuples == expected_logs

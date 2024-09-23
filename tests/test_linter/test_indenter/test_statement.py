# Copyright (c) 2021-2024 Arista Networks, Inc.
# Use of this source code is governed by the MIT license
# that can be found in the LICENSE file.
"""
Tests for j2lint.linter.indenter.statement.py

To understand the values given to this class it is paramount to read
j2lint.utils.get_jinja_statement as this is the path in the code
that will parse a file content and return a list of statements - abusively called lines
"""

import pytest

from j2lint.linter.indenter.statement import JinjaStatement


class TestJinjaStatement:
    @pytest.mark.parametrize(
        "line, expected_statement",
        [
            pytest.param(
                (
                    " if switch.platform_settings.tcam_profile is arista.avd.defined ",
                    2,
                    2,
                    "{%",
                    "%}",
                ),
                {
                    "begin": 1,
                    "words": [
                        "if",
                        "switch.platform_settings.tcam_profile",
                        "is",
                        "arista.avd.defined",
                    ],
                    "start_line_no": 2,
                    "end_line_no": 2,
                    "start_delimiter": "{%",
                    "end_delimiter": "%}",
                },
                id="working statement",
            ),
            # this next one is failing because we never expect to be called
            # with an empty list probably should be caught in __init__
            # if we even keep the class..
            # pytest.param("[]", {}, id="empty_statement"),
        ],
    )
    def test_jinja_statement(self, line, expected_statement):
        """ """
        # TODO - why is it not an __init__ method???
        statement = JinjaStatement(line)
        for key, value in expected_statement.items():
            assert statement.__getattribute__(key) == value

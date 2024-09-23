# Copyright (c) 2021-2024 Arista Networks, Inc.
# Use of this source code is governed by the MIT license
# that can be found in the LICENSE file.
"""Tests for j2lint.utils.py"""

import pathlib

import pytest

from j2lint.utils import (
    delimit_jinja_statement,
    flatten,
    get_files,
    get_tuple,
    is_rule_disabled,
    is_valid_file_type,
)

from .utils import does_not_raise

# pylint: disable=fixme


@pytest.mark.skip
def test_load_plugins() -> None:
    """
    Test the utils.load_plugins function.

    For now this is being tested via other calling methods
    """


@pytest.mark.parametrize(
    ("file_name", "extensions", "expected"),
    [
        ("test.j2", [".j2", ".jinja2", ".jinja"], True),
        ("test.jinja", [".j2", ".jinja2", ".jinja"], True),
        ("test.jinja2", [".j2", ".jinja2", ".jinja"], True),
        ("test.blah", [".j2", ".jinja2", ".jinja"], False),
        ("test_dir/test.j2", [".j2", ".jinja2", ".jinja"], True),
        ("test", [".j2", ".jinja2", ".jinja"], False),
        ("test.toto", [".toto"], True),
        ("test.j2", [".toto"], False),
    ],
)
def test_is_valid_file_type(file_name: str, extensions: list[str], expected: bool) -> None:
    """Test the utils.is_valid_file_type function."""
    assert is_valid_file_type(file_name, extensions) == expected


@pytest.mark.parametrize(
    "file_or_dir_names, extensions, expected_value, expectation",
    [
        (["test.j2"], [".j2", ".jinja2", ".jinja"], ["test.j2"], does_not_raise()),
        (
            ["test.jinja"],
            [".j2", ".jinja2", ".jinja"],
            ["test.jinja"],
            does_not_raise(),
        ),
        (
            ["test.jinja2"],
            [".j2", ".jinja2", ".jinja"],
            ["test.jinja2"],
            does_not_raise(),
        ),
        (
            ["test.jinja", "test.j2"],
            [".j2", ".jinja2", ".jinja"],
            ["test.jinja", "test.j2"],
            does_not_raise(),
        ),
        (
            ["test.blah"],
            [".j2", ".jinja2", ".jinja"],
            [],
            does_not_raise(),
        ),
        (
            ["test.html"],
            [".html"],
            ["test.html"],
            does_not_raise(),
        ),
        (
            ["test_dir/test.j2"],
            [".j2", ".jinja2", ".jinja"],
            ["test_dir/test.j2"],
            does_not_raise(),
        ),
        (["test"], [".j2", ".jinja2", ".jinja"], [], does_not_raise()),
        pytest.param("not_a_list", None, None, pytest.raises(TypeError), id="Invalid input type"),
    ],
)
def test_get_files(file_or_dir_names, extensions, expected_value, expectation):
    """
    Test the utils.get_files function
    """
    with expectation:
        assert get_files(file_or_dir_names, extensions) == expected_value


def test_get_files_dir(template_tmp_dir):
    """
    Test the utils.get_files function

    # sadly cannot use fixture in parametrize...
    # https://github.com/pytest-dev/pytest/issues/349
    """
    tmp_dir = pathlib.Path(__file__).parent / "tmp"  # as passed to pytest in pytest.ini
    expected = sorted(
        [
            f"{tmp_dir}/rules/rules.j2",
            f"{tmp_dir}/rules/rules_subdir/rules.j2",
            f"{tmp_dir}/rules/.rules_hidden_subdir/rules.j2",
        ]
    )
    with does_not_raise():
        assert sorted(get_files(template_tmp_dir, [".j2"])) == expected


@pytest.mark.parametrize(
    "input_list, expected, raising_context",
    [
        ("not_a_list", [], pytest.raises(TypeError)),
        ([1, 2, 3], [1, 2, 3], does_not_raise()),
        ([1, 2, [3, 4]], [1, 2, 3, 4], does_not_raise()),
        ([[1, 2], [3, 4]], [1, 2, 3, 4], does_not_raise()),
    ],
)
def test_flatten(input_list, expected, raising_context):
    """
    Test the utils.flatten function
    """
    with raising_context:
        assert list(flatten(input_list)) == expected


@pytest.mark.parametrize(
    "tuple_list, lookup_object, expected_value",
    [
        (
            [(1, 2, 3), (1, 2, 4)],
            1,
            (1, 2, 3),
        ),  # test that we get the first tuple that matches
        ([(1, 2, 3), (1, 2, 4)], 4, (1, 2, 4)),
        ([], 4, None),
        ([(1, 2, 3), (1, 2, 4)], 5, None),
    ],
)
def test_get_tuple(tuple_list, lookup_object, expected_value):
    """
    Test the utils.get_tuple function
    """
    assert get_tuple(tuple_list, lookup_object) == expected_value


@pytest.mark.skip
def test_get_jinja_statements():
    """
    Test the utils.get_jinja_statements function
    """
    # TODO


@pytest.mark.parametrize(
    "line, kwargs, expected",
    [
        ("foo", {}, "{%foo%}"),
        ("foo", {"start": "{#"}, "{#foo%}"),
        ("foo", {"start": "{#", "end": "#}"}, "{#foo#}"),
    ],
)
def test_delimit_jinja_statement(line, kwargs, expected):
    """
    Test the utils.delimit_jinja_statement function
    """
    assert delimit_jinja_statement(line, **kwargs) == expected


@pytest.mark.skip
def test_get_jinja_comments():
    """
    Test the utils.get_jinja_comments function
    """
    # TODO


@pytest.mark.skip
def test_get_jinja_variables():
    """
    Test the utils.get_jinja_variables function
    """
    # TODO


@pytest.mark.parametrize(
    "comments, expected_value",
    [
        pytest.param(["{# j2lint: disable=test-rule-0 #}"], True, id="found_short_description"),
        pytest.param(["{# j2lint: disable=T0 #}"], True, id="found_id"),
        pytest.param(
            ["{# j2lint: disable=test-rule-1 #}"],
            False,
            id="not_found_short_description",
        ),
        pytest.param(["{# j2lint: disable=T1 #}"], False, id="not_found_id"),
        pytest.param(
            ["{# j2lint: disable=dummy-rule, test-rule-0 #}"],
            False,
            id="NOT_SUPPORTED_single_comment_list",
        ),
        pytest.param(
            ["{# j2lint: disable=dummy-rule, j2lint: disable=test-rule-0 #}"],
            True,
            id="single_comment_repeat_pattern",
        ),
        pytest.param(
            ["{# j2lint: disable=dummy-rule #}", "{# j2lint: disable=test-rule-0 #}"],
            True,
            id="found_second_second_syntax",
        ),
    ],
)
def test_is_rule_disabled(make_rules, comments, expected_value):
    """
    Test the utils.is_rule_disabled function
    """
    # Generate one rule through fixture which is always
    # T0, test-rule-0
    test_rule = make_rules(1)[0]

    comments_string = "\n".join(comments)
    print(comments_string)
    assert is_rule_disabled(comments_string, test_rule) == expected_value

# Copyright (c) 2021-2026 Arista Networks, Inc.
# Use of this source code is governed by the MIT license
# that can be found in the LICENSE file.
"""Tests for j2lint.utils.py."""

from __future__ import annotations

from contextlib import nullcontext as does_not_raise
from pathlib import Path
from typing import TYPE_CHECKING, Any

import pytest

from j2lint.utils import (
    delimit_jinja_statement,
    flatten,
    get_files,
    get_jinja_comments,
    get_jinja_expressions,
    get_jinja_statements,
    get_raw_block_ranges,
    get_tuple,
    is_rule_disabled,
    is_valid_file_type,
    mask_raw_block_contents,
)

if TYPE_CHECKING:
    from collections.abc import Callable
    from contextlib import AbstractContextManager

    from j2lint.linter.rule import Rule


@pytest.mark.skip
def test_load_plugins() -> None:
    """Test the utils.load_plugins function.

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
def test_is_valid_file_type(file_name: str, extensions: list[str], *, expected: bool) -> None:
    """Test the utils.is_valid_file_type function."""
    assert is_valid_file_type(Path(file_name), extensions) == expected


@pytest.mark.parametrize(
    ("file_or_dir_names", "extensions", "expected_value", "expectation"),
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
def test_get_files(file_or_dir_names: list[str], extensions: list[str], expected_value: list[str], expectation: AbstractContextManager[str]) -> None:
    """Test the utils.get_files function."""
    with expectation:
        paths = [Path(file_or_dir_name) for file_or_dir_name in file_or_dir_names]
        assert [str(filepath) for filepath in get_files(paths, extensions)] == expected_value


def test_get_files_dir(template_tmp_dir: str) -> None:
    """Test the utils.get_files function.

    # sadly cannot use fixture in parametrize...
    # https://github.com/pytest-dev/pytest/issues/349
    """
    tmp_dir = Path(__file__).parent / "tmp"  # as passed to pytest in pytest.ini
    expected = sorted(
        [
            f"{tmp_dir}/rules/rules.j2",
            f"{tmp_dir}/rules/rules_subdir/rules.j2",
            f"{tmp_dir}/rules/.rules_hidden_subdir/rules.j2",
        ]
    )
    with does_not_raise():
        paths = [Path(file) for file in template_tmp_dir]
        assert sorted([str(filename) for filename in get_files(paths, [".j2"])]) == expected


@pytest.mark.parametrize(
    ("input_list", "expected", "raising_context"),
    [
        ("not_a_list", [], pytest.raises(TypeError)),
        ([1, 2, 3], [1, 2, 3], does_not_raise()),
        ([1, 2, [3, 4]], [1, 2, 3, 4], does_not_raise()),
        ([[1, 2], [3, 4]], [1, 2, 3, 4], does_not_raise()),
    ],
)
def test_flatten(input_list: list[list[Any]], expected: list[Any], raising_context: AbstractContextManager[str]) -> None:
    """Test the utils.flatten function."""
    with raising_context:
        assert list(flatten(input_list)) == expected


@pytest.mark.parametrize(
    ("tuple_list", "lookup_object", "expected_value"),
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
def test_get_tuple(tuple_list: list[tuple[Any]], lookup_object: Any, expected_value: tuple[Any] | None) -> None:
    """Test the utils.get_tuple function."""
    assert get_tuple(tuple_list, lookup_object) == expected_value


@pytest.mark.parametrize(
    ("text", "indentation", "expected"),
    [
        pytest.param(
            "{% if foo %}\n{% endif %}",
            False,
            [(" if foo ", 1, 1, "{%", "%}"), (" endif ", 2, 2, "{%", "%}")],
            id="simple statements",
        ),
        pytest.param(
            "{%- if foo -%}\n{% endif %}",
            False,
            [(" if foo ", 1, 1, "{%-", "-%}"), (" endif ", 2, 2, "{%", "%}")],
            id="trimmed delimiters",
        ),
        pytest.param(
            "prefix {% if foo %}\n{% endif %}",
            False,
            [(" if foo ", 1, 1, "{%", "%}"), (" endif ", 2, 2, "{%", "%}")],
            id="inline statement included by default",
        ),
        pytest.param(
            "prefix {% if foo %}\n{% endif %}",
            True,
            [(" endif ", 2, 2, "{%", "%}")],
            id="indentation mode skips inline statement",
        ),
        pytest.param(
            "{% if foo\n   and bar %}\n{% endif %}",
            True,
            [(" if foo\n   and bar ", 1, 2, "{%", "%}"), (" endif ", 3, 3, "{%", "%}")],
            id="indentation mode keeps multiline statement",
        ),
    ],
)
def test_get_jinja_statements(text: str, *, indentation: bool, expected: list[tuple[str, int, int, str, str]]) -> None:
    """Test the utils.get_jinja_statements function."""
    assert get_jinja_statements(text, indentation=indentation) == expected


def test_get_jinja_statements_ignores_raw_block_content() -> None:
    """Test that raw block content is ignored while raw tags remain visible."""
    text = "{% raw %}\n{% if hidden %}\n{% endraw %}\n{% if shown %}\n{% endif %}"

    assert [statement[0].strip() for statement in get_jinja_statements(text)] == ["raw", "endraw", "if shown", "endif"]


def test_get_jinja_statements_ignores_raw_block_content_on_same_line() -> None:
    """Test that same-line raw content is ignored while later statements still count."""
    text = "{% raw %} {% if blah %} {% endif %} {% endraw %} {% if bloh %} toto {% endif %}"

    assert [statement[0].strip() for statement in get_jinja_statements(text)] == ["raw", "endraw", "if bloh", "endif"]


@pytest.mark.parametrize(
    ("line", "kwargs", "expected"),
    [
        ("foo", {}, "{%foo%}"),
        ("foo", {"start": "{#"}, "{#foo%}"),
        ("foo", {"start": "{#", "end": "#}"}, "{#foo#}"),
    ],
)
def test_delimit_jinja_statement(line: str, kwargs: dict[str, str], expected: str) -> None:
    """Test the utils.delimit_jinja_statement function."""
    assert delimit_jinja_statement(line, **kwargs) == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        pytest.param("plain text", [], id="no comments"),
        pytest.param("{# visible #}", [" visible "], id="single comment"),
        pytest.param("foo {# inline #} bar", [" inline "], id="inline comment"),
        pytest.param("{# first #}\n{# second line 1\nsecond line 2 #}", [" first ", " second line 1\nsecond line 2 "], id="multiple comments"),
    ],
)
def test_get_jinja_comments(text: str, expected: list[str]) -> None:
    """Test the utils.get_jinja_comments function."""
    assert get_jinja_comments(text) == expected


def test_get_jinja_comments_ignores_raw_block_content() -> None:
    """Test that Jinja comments inside raw blocks are ignored."""
    text = "{# visible #}\n{% raw %}\n{# hidden #}\n{% endraw %}\n{# also visible #}"

    assert get_jinja_comments(text) == [" visible ", " also visible "]


@pytest.mark.parametrize(
    ("test_template", "blank_literals", "expected"),
    [
        pytest.param("foo {{}} bar", False, [""], id="empty string"),
        pytest.param("a valid simple line - foo, bar, baz, qux, quux", False, [], id="no expressions"),
        pytest.param("a valid line with two variables - foo, {{ valid_1 }}, baz, qux, {{ valid_2 }}", False, [" valid_1 ", " valid_2 "], id="simple expressions"),
        pytest.param("{{foo}}{{ bar }}", False, ["foo", " bar "], id="adjacent expressions"),
        pytest.param(
            "a valid line with filters - foo, {{ valid_1 | default ('bar') }}, baz, qux, {{ valid_2 | capitalize }}",
            False,
            [" valid_1 | default ('bar') ", " valid_2 | capitalize "],
            id="with filters",
        ),
        pytest.param(
            """
            a valid simple line - foo, bar, baz, qux, quux a valid line with two variables - foo, {{ valid_1 }}, baz, qux, {{ valid_2 }}
            a valid line with filters - foo, {{ valid_1 | default ('bar') }}, baz, qux, {{ valid_2 | capitalize }}
            """,
            False,
            [" valid_1 ", " valid_2 ", " valid_1 | default ('bar') ", " valid_2 | capitalize "],
            id="multiline",
        ),
        pytest.param(
            """
            {{ foo['bar'] ~ ' baz qux ' ~ foo['bar'] }}
            {{ 'foo bar: ' ~ baz.qux }}
            {{ quux(foo, 'bar', "qux") }}
            """,
            True,
            [" foo[''] ~ '' ~ foo[''] ", " '' ~ baz.qux ", " quux(foo, '', \"\") "],
            id="complex",
        ),
        pytest.param(
            """
            {{ foo['bar'] ~ ' baz qux ' ~ foo['bar'] }}
            {{ 'foo bar: ' ~ baz.qux }}
            {{ quux(foo, 'bar', "qux") }}
            """,
            False,
            [" foo['bar'] ~ ' baz qux ' ~ foo['bar'] ", " 'foo bar: ' ~ baz.qux ", " quux(foo, 'bar', \"qux\") "],
            id="complex don't remove strings",
        ),
        pytest.param("foo {{ 'bar' }} baz {{ \"qux\" }}", False, [" 'bar' ", ' "qux" '], id="strings left in"),
        pytest.param("foo {{ 'bar' }} baz {{ \"qux\" }}", True, [" '' ", ' "" '], id="strings removed"),
        pytest.param("{{ foo ~ inner_func('bar', \"baz\") }}", True, [" foo ~ inner_func('', \"\") "], id="functions"),
        pytest.param("{{ foo('bar \\'baz\\' qux', \"quux \\\"foo\\\" bar\") }}", True, [" foo('', \"\") "], id="complex 2"),
        pytest.param(
            "{{ foo('bar \\'baz\\' qux', \"quux \\\"foo\\\" bar\") }}",
            False,
            [" foo('bar \\'baz\\' qux', \"quux \\\"foo\\\" bar\") "],
            id="complex 2 don't remove strings",
        ),
        pytest.param(
            "{% raw %}{{ hidden_value }}{% endraw %} {{ visible_value }}",
            False,
            [" visible_value "],
            id="ignore raw block expressions",
        ),
    ],
)
def test_get_jinja_expressions(test_template: str, blank_literals: bool, expected: list[str]) -> None:  # noqa: FBT001
    """Test the utils.get_jinja_expressions function."""
    assert get_jinja_expressions(test_template, blank_literals=blank_literals) == expected


@pytest.mark.parametrize(
    ("text", "expected_segments"),
    [
        pytest.param(
            "{{ variable }}",
            [],
            id="no raw blocks",
        ),
        pytest.param(
            "{% raw %}{{ foo }}{% endraw %}",
            ["{{ foo }}"],
            id="single line raw block",
        ),
        pytest.param(
            "{%- raw %}{{ foo }}{%- endraw %}",
            ["{{ foo }}"],
            id="single line trimmed raw block",
        ),
        pytest.param(
            "{%%}{% raw %}{{ foo }}{% endraw %}",
            ["{{ foo }}"],
            id="ignore empty statements before raw block",
        ),
        pytest.param(
            "{% raw %}\n{{ foo }}\n{% endraw %}\n{% raw %}{{ bar }}",
            ["\n{{ foo }}\n", "{{ bar }}"],
            id="multiple and unterminated raw blocks",
        ),
    ],
)
def test_get_raw_block_ranges(text: str, expected_segments: list[str]) -> None:
    """Test the utils.get_raw_block_ranges function."""
    assert [text[start:end] for start, end in get_raw_block_ranges(text)] == expected_segments


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        pytest.param(
            "{{ variable }}",
            "{{ variable }}",
            id="no raw blocks",
        ),
        pytest.param(
            "{% raw %}{{ foo }}{% endraw %}",
            "{% raw %}         {% endraw %}",
            id="single line raw block",
        ),
        pytest.param(
            "{% raw %}\n{{ foo }}\n{% endraw %}\n{{ bar }}",
            "{% raw %}\n         \n{% endraw %}\n{{ bar }}",
            id="multiline raw block",
        ),
    ],
)
def test_mask_raw_block_contents(text: str, expected: str) -> None:
    """Test the utils.mask_raw_block_contents function."""
    assert mask_raw_block_contents(text) == expected


@pytest.mark.parametrize(
    ("comments", "expected_value"),
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
        pytest.param(
            ["{% raw %}", "{# j2lint: disable=test-rule-0 #}", "{% endraw %}"],
            False,
            id="ignore_comments_inside_raw_blocks",
        ),
    ],
)
def test_is_rule_disabled(make_rules: Callable[[int], list[Rule]], comments: list[str], *, expected_value: bool) -> None:
    """Test the utils.is_rule_disabled function."""
    # Generate one rule through fixture which is always
    # T0, test-rule-0
    test_rule = make_rules(1)[0]

    comments_string = "\n".join(comments)
    assert is_rule_disabled(comments_string, test_rule) == expected_value

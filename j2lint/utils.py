# Copyright (c) 2021-2025 Arista Networks, Inc.
# Use of this source code is governed by the MIT license
# that can be found in the LICENSE file.
"""utils.py - Utility functions for jinja2 linter."""

from __future__ import annotations

import importlib.util
import os
import re
from collections.abc import Generator, Iterable
from pathlib import Path
from typing import TYPE_CHECKING, Any

from j2lint.logger import logger

if TYPE_CHECKING:
    from .linter.rule import Rule

# Statement type is a tuple (line_without_delimiter, start_line, end_line, start_delimiter, end_delimiter)
Statement = tuple[str, int, int, str, str]


def load_plugins(directory: Path) -> list[Rule]:
    """Load and execute all the Rule modules from the specified directory.

    Parameters
    ----------
    directory : Path
        Loads the modules a directory

    Returns
    -------
    list
        List of rule classes
    """
    result = []
    file_handle = None
    for plugin_file in directory.glob(pattern="[A-Za-z_]*.py"):
        plugin_name = plugin_file.name.replace(".py", "")
        try:
            logger.debug("Loading plugin %s", plugin_name)
            spec = importlib.util.spec_from_file_location(plugin_name, plugin_file)
            if plugin_name != "__init__" and spec is not None:
                class_name = "".join(str(name).capitalize() for name in plugin_name.split("_"))
                module = importlib.util.module_from_spec(spec)
                if spec.loader is not None:
                    spec.loader.exec_module(module)
                    obj = getattr(module, class_name)()
                    result.append(obj)
        except AttributeError:
            logger.warning("Failed to load plugin %s", plugin_name)
        finally:
            if file_handle:
                file_handle.close()
    return result


def is_valid_file_type(filename: Path, extensions: list[str]) -> bool:
    """Check if the file extension is in the list of accepted extensions.

    Parameters
    ----------
    filename
        File path with extension
    extensions
        List of file extensions to look for

    Returns
    -------
    boolean
        True if file type is correct
    """
    extension = filename.suffix.lower()
    return extension in extensions


def get_files(file_or_dir_names: list[Path], extensions: list[str]) -> list[Path]:
    """Get files from a directory recursively.

    Parameters
    ----------
    file_or_dir_names
        List of directories and files
    extensions
        List of file extensions to look for

    Returns
    -------
    list
        List of file paths
    """
    file_paths: list[Path] = []

    if not isinstance(file_or_dir_names, (list, set)):
        msg = f"get_files expects a list or a set and got {file_or_dir_names}"
        raise TypeError(msg)

    for file_or_dir in file_or_dir_names:
        file_or_dir_path = file_or_dir
        if file_or_dir_path.is_dir():
            for root, _, files in os.walk(str(file_or_dir_path)):
                root_path = Path(root)
                for file in files:
                    file_path = root_path / file
                    if is_valid_file_type(file_path, extensions):
                        file_paths.append(file_path)
        elif is_valid_file_type(file_or_dir_path, extensions):
            file_paths.append(file_or_dir_path)
    logger.debug("Linting directory %s: files %s", file_or_dir_names, file_paths)
    return file_paths


def flatten(nested_list: Iterable[Any]) -> Generator[Any, Any, Any]:
    """Flatten an iterable.

    Parameters
    ----------
    nested_list
        Nested list

    Returns
    -------
    Generator[Any, Any, Any]
        a generator that yields the elements of each object in the nested_list
    """
    if not isinstance(nested_list, (list, tuple)):
        msg = f"flatten is expecting a list or tuple and received {nested_list}"
        raise TypeError(msg)
    for element in nested_list:
        if isinstance(element, Iterable) and not isinstance(element, (str, bytes)):
            yield from flatten(element)
        else:
            yield element


def get_tuple(list_of_tuples: list[tuple[Any, ...]], item: Any) -> tuple[Any, ...] | None:  # noqa: ANN401
    """Check if an item is present in any of the tuples.

    Parameters
    ----------
    list_of_tuples
        list of tuples
    item
        single object which can be in a tuple

    Returns
    -------
    tuple | None
        tuple if the item exists in any of the tuples
    """
    return next((entry for entry in list_of_tuples if item in entry), None)


def get_jinja_statements(text: str, *, indentation: bool = False) -> list[Statement]:
    """Get jinja statements with {%[-/+] [-]%} delimiters.

    The regex `regex_pattern` will return multiple groups when it matches
    Note that this is a multiline regex

    # TODO - should probably return a JinjaStatement object..

    Parameters
    ----------
    text
        multiline text to search the jinja statements in.
    indentation
        Set to True if parsing for indentation, it will allow to retrieve multiple lines.

    Examples
    --------
    For this given template:

    ```
    {# tcam-profile #}
    {% if switch.platform_settings.tcam_profile is arista.avd.defined %}
    tcam_profile:
      system: {{ switch.platform_settings.tcam_profile }}
    {% endif %}
    ```

    With `indentation=True`:

    ```
    Found jinja statements [(' if switch.platform_settings.tcam_profile
    is arista.avd.defined ', 2, 2, '{%', '%}'), (' endif ', 5, 5, '{%', '%}')]
    ```

    With `indentation=False`

    ```
    Found jinja statements []
    Found jinja statements [(' if switch.platform_settings.tcam_profile is
    arista.avd.defined ', 1, 1, '{%', '%}')]
    Found jinja statements []
    Found jinja statements []
    Found jinja statements [(' endif ', 1, 1, '{%', '%}')]
    Found jinja statements []
    ```

    Returns
    -------
    list
        List of jinja statements
    """
    statements: list[Statement] = []
    count = 0
    regex_pattern = re.compile("(\\{%[-|+]?)((.|\n)*?)([-]?\\%})", re.MULTILINE)
    newline_pattern = re.compile(r"\n")
    lines = text.split("\n")
    for match in regex_pattern.finditer(text):
        count += 1
        start_line = len(newline_pattern.findall(text, 0, match.start(2))) + 1
        end_line = len(newline_pattern.findall(text, 0, match.end(2))) + 1
        if indentation and lines[start_line - 1].split()[0] not in ["{%", "{%-", "{%+"]:
            continue

        statements.append(
            (
                str(match.group(2)),
                start_line,
                end_line,
                str(match.group(1)),
                str(match.group(4)),
            )
        )
    logger.debug("Found jinja statements %s", statements)
    return statements


def delimit_jinja_statement(line: str, start: str = "{%", end: str = "%}") -> str:
    """Add start and end delimiters for a jinja statement.

    Parameters
    ----------
    line
        Text line
    start
        Start delimiter
    end
        End delimiter

    Returns
    -------
    str
        Jinja statement with jinja start and end delimiters
    """
    return start + line + end


def get_jinja_comments(text: str) -> list[str]:
    """Get jinja comments.

    Parameters
    ----------
    text
        Text to get jinja comments

    Returns
    -------
    list
        List of jinja comments
    """
    regex_pattern = re.compile("(\\{#)((.|\n)*?)(\\#})", re.MULTILINE)

    return [line.group(2) for line in regex_pattern.finditer(text)]


def get_jinja_expressions(text: str, *, blank_literals: bool = False) -> list[str]:
    """Get jinja expressions.

    Parameters
    ----------
    text
        Text to get jinja expressions
    blank_literals
        Set to True to replace string literals with blank (empty) values

    Examples
    --------
    For this given template:

    ```
    User info: {{ 'Hello, ' + user.name }}
    ```

    With `blank_literals=False`:

    ```
    [" 'Hello, ' + user.name "]
    ```

    With `blank_literals=True`:

    ```
    [" '' + user.name "]
    ```

    Returns
    -------
    list
        List of jinja expressions (optionally with string literals blanked)
    """
    regex_pattern = re.compile("(\\{{)((.|\n)*?)(\\}})", re.MULTILINE)

    exps_strings_intact = [line.group(2) for line in regex_pattern.finditer(text)]

    if blank_literals:
        # Replace string literals with empty strings
        exps_strings_blanked = []
        for exp in exps_strings_intact:
            # Replace single and double quoted strings with empty strings inc. nested
            single_quote_pattern = re.compile(r"'(?:\\.|[^'\\])*'")
            double_quote_pattern = re.compile(r"\"(?:\\.|[^\"\\])*\"")

            exp_blanked_no_double_quotes = re.sub(double_quote_pattern, '""', exp)
            exp_fully_blanked = re.sub(single_quote_pattern, "''", exp_blanked_no_double_quotes)

            exps_strings_blanked.append(exp_fully_blanked)
        return exps_strings_blanked
    return exps_strings_intact


def is_rule_disabled(text: str, rule: Rule) -> bool:
    """Check if rule is disabled.

    Parameters
    ----------
    text
        Text to check
    rule
        Rule object

    Returns
    -------
    boolean
        True if rule is disabled
    """
    comments = get_jinja_comments(text)
    regex = re.compile(r"j2lint\s*:\s*disable\s*=\s*([\w-]+)")
    for comment in comments:
        for line in regex.finditer(comment):
            if rule.short_description == line.group(1):
                return True
            if rule.rule_id == line.group(1):
                return True
    return False

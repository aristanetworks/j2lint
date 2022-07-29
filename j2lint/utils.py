"""utils.py - Utility functions for jinja2 linter.
"""
import glob
import importlib.util
import os
import re

from collections.abc import Iterable

from j2lint.logger import logger

LANGUAGE_JINJA = "jinja"


def load_plugins(directory):
    """Loads and executes all the Rule modules from the specified directory

    Args:
        directory (string): Loads the modules a directory

    Returns:
        list: List of rule classes
    """
    result = []
    file_handle = None
    for plugin_file in glob.glob(os.path.join(directory, "[A-Za-z_]*.py")):
        plugin_name = os.path.basename(plugin_file.replace(".py", ""))
        try:
            logger.debug("Loading plugin %s", plugin_name)
            spec = importlib.util.spec_from_file_location(
                plugin_name, plugin_file)
            if plugin_name != "__init__":
                class_name = "".join(
                    str(name).capitalize() for name in plugin_name.split("_")
                )
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                obj = getattr(module, class_name)()
                result.append(obj)
        except AttributeError:
            logger.warning("Failed to load plugin %s", plugin_name)
        finally:
            if file_handle:
                file_handle.close()
    return result


def is_valid_file_type(file_name):
    """Checks if the file is a valid Jinja file

    Args:
        file_name (string): file path with extension

    Returns:
        boolean: True if file type is correct
    """
    extension = os.path.splitext(file_name)[1].lower()
    if extension in [".jinja", ".jinja2", ".j2"]:
        return True
    return False


def get_file_type(file_name):
    """Returns file type as Jinja or None

    Args:
        file_name (string): file path with extension

    Returns:
        string: jinja or None

    TODO: this method and the previous one are redundant
    """
    if is_valid_file_type(file_name):
        return LANGUAGE_JINJA
    return None


def get_files(file_or_dir_names):
    """Get files from a directory recursively

    Args:
        file_or_dir_names (list): list of directories and files

    Returns:
        list: list of file paths
    """
    file_paths = []

    if not isinstance(file_or_dir_names, (list, set)):
        raise TypeError(
            f"get_files expects a list or a set and got {file_or_dir_names}"
        )

    for file_or_dir in file_or_dir_names:
        if os.path.isdir(file_or_dir):
            for root, _, files in os.walk(file_or_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    if get_file_type(file_path) == LANGUAGE_JINJA:
                        file_paths.append(file_path)
        else:
            if get_file_type(file_or_dir) == LANGUAGE_JINJA:
                file_paths.append(file_or_dir)
    logger.debug("Linting directory %s: files %s",
                 file_or_dir_names, file_paths)
    return file_paths


def flatten(nested_list):
    """Flattens an iterable

    Args:
        nested_list (list): Nested list

    Yields:
        list: flattened list
    """
    if not isinstance(nested_list, (list, tuple)):
        raise TypeError(
            f"flatten is expecting a list or tuple and received {nested_list}")
    for element in nested_list:
        if isinstance(element, Iterable) and not isinstance(element, (str, bytes)):
            yield from flatten(element)
        else:
            yield element


def get_tuple(list_of_tuples, item):
    """Checks if an item is present in any of the tuples

    Args:
        list_of_tuples (list): list of tuples
        item (object): single object which can be in a tuple

    Returns:
        [tuple]: tuple if the item exists in any of the tuples
    """
    for entry in list_of_tuples:
        if item in entry:
            return entry
    return None


def get_jinja_statements(text, indentation=False):
    """Gets jinja statements with {%[-/+] [-]%} delimiters

    The regex `regex_pattern` will return multiple groups when it matches
    Note that this is a multiline regex

    Args:
        text (string): multiline text to search the jinja statements in
        indentation (bool): Set to True if parsing for indentation, it will allow
                            to retrieve multiple lines
    Example:

    For this given template:

        {# tcam-profile #}
        {% if switch.platform_settings.tcam_profile is arista.avd.defined %}
        tcam_profile:
          system: {{ switch.platform_settings.tcam_profile }}
        {% endif %}

    With indentation=True

        Found jinja statements [(' if switch.platform_settings.tcam_profile
        is arista.avd.defined ', 2, 2, '{%', '%}'), (' endif ', 5, 5, '{%', '%}')]

    With indentation=False

        Found jinja statements []
        Found jinja statements [(' if switch.platform_settings.tcam_profile is
        arista.avd.defined ', 1, 1, '{%', '%}')]
        Found jinja statements []
        Found jinja statements []
        Found jinja statements [(' endif ', 1, 1, '{%', '%}')]
        Found jinja statements []

    Returns:
        [list]: list of jinja statements
    """
    statements = []
    count = 0
    regex_pattern = re.compile(
        "(\\{%[-|+]?)((.|\n)*?)([-]?\\%})", re.MULTILINE)
    newline_pattern = re.compile(r"\n")
    lines = text.split("\n")
    for match in regex_pattern.finditer(text):
        count += 1
        start_line = len(newline_pattern.findall(text, 0, match.start(2))) + 1
        end_line = len(newline_pattern.findall(text, 0, match.end(2))) + 1
        if indentation and lines[start_line - 1].split()[0] not in ["{%", "{%-", "{%+"]:
            continue
        statements.append(
            (match.group(2), start_line, end_line, match.group(1), match.group(4))
        )
    logger.debug("Found jinja statements %s", statements)
    return statements


def delimit_jinja_statement(line, start="{%", end="%}"):
    """Adds end delimiters for a jinja statement

    Args:
        line (string): text line

    Returns:
        [string]: jinja statement with jinja start and end delimiters
    """
    return start + line + end


def get_jinja_comments(text):
    """Gets jinja comments

    Args:
        line (string): text to get jinja comments

    Returns:
        [list]: returns list of jinja comments
    """
    comments = []
    regex_pattern = re.compile("(\\{#)((.|\n)*?)(\\#})", re.MULTILINE)
    for line in regex_pattern.finditer(text):
        comments.append(line.group(2))
    return comments


def get_jinja_variables(text):
    """Gets jinja variables

    Args:
        line (string): text to get jinja variables

    Returns:
        [list]: returns list of jinja variables
    """
    variables = []
    regex_pattern = regex_pattern = re.compile(
        "(\\{{)((.|\n)*?)(\\}})", re.MULTILINE)
    for line in regex_pattern.finditer(text):
        variables.append(line.group(2))
    return variables


def is_rule_disabled(text, rule):
    """Check if rule is disabled

    Args:
        text (string): text to check jinja comments
        rule (string): rule id or description

    Returns:
        [boolean]: True if rule is disabled
    """
    comments = get_jinja_comments(text)
    regex = re.compile(r"j2lint\s*:\s*disable\s*=\s*([\w-]+)")
    for comment in comments:
        for line in regex.finditer(comment):
            if rule.short_description == line.group(1):
                return True
            if rule.id == line.group(1):
                return True
    return False

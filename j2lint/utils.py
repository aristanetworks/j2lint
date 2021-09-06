import glob
import importlib.util
import os
import re
import collections

LANGUAGE_JINJA = "jinja"


def load_plugins(directory):
    """ Loads and executes all the Rule modules from the specified directory """
    result = []
    file_handle = None

    for pluginfile in glob.glob(os.path.join(directory, '[A-Za-z]*.py')):
        pluginname = os.path.basename(pluginfile.replace('.py', ''))
        try:
            spec = importlib.util.spec_from_file_location(
                pluginname, pluginfile)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            obj = getattr(module, pluginname)()
            result.append(obj)
        finally:
            if file_handle:
                file_handle.close()
    return result


def is_valid_file_type(file_name):
    """ Checks if the file is a valid Jinja file """
    extension = os.path.splitext(file_name)[1].lower()
    if extension in [".jinja", ".jinja2", ".j2"]:
        return True
    return False


def get_file_type(file_name):
    """ Returns file type as Jinja or None """
    if is_valid_file_type(file_name):
        return LANGUAGE_JINJA
    return None


def get_jinja_files(file_or_dir_names):
    """Get files from a directory """
    file_paths = []

    for file_or_dir in file_or_dir_names:
        if os.path.isdir(file_or_dir):
            for root, dirs, files in os.walk(file_or_dir):
                for f in files:
                    file_path = os.path.join(root, f)
                    file_paths.append(file_path)
        else:
            file_paths.append(file_or_dir)
    return file_paths


def flatten(l):
    """
    Deeply flattens an iterable.
    """
    for el in l:
        if (isinstance(el, collections.Iterable) and
                not isinstance(el, (str, bytes))):
            yield from flatten(el)
        else:
            yield el


def get_tuple(l, item):
    for entry in l:
        if item in entry:
            return entry
    return None


def get_jinja_statements(text):
    statements = []
    count = 0
    regex_pattern = re.compile("\\{%(.*?)\\%}")
    newline_pattern = re.compile(r'\n')
    for m in regex_pattern.finditer(text):
        count += 1
        start_line = len(newline_pattern.findall(text, 0, m.start(1)))+1
        end_line = len(newline_pattern.findall(text, 0, m.end(1)))+1
        statements.append((m.group(1), start_line, end_line))
    return statements


def delimit_jinja_statement(line):
    return "{%" + line + "%}"

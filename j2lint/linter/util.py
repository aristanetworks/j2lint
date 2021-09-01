import collections
import re


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

"""statement.py - Class and variables for jinja statements.
"""
import re
JINJA_STATEMENT_TAG_NAMES = [
    ('for', 'else', 'endfor'),
    ('if', 'elif', 'else', 'endif'),
    ('macro', 'endmacro'),
]

class JinjaStatement:
    """Class for representing a jinja statement.
    """
    begin = None
    words = []

    def __init__(self, line):
        whitespaces = re.findall('\s*', line[0])

        self.begin = len(whitespaces[0])
        self.line = line[0]
        self.words = line[0].split()
        self.start_line_no = line[1]
        self.end_line_no = line[2]
        self.start_delimeter = line[3]
        self.end_delimeter = line[4]

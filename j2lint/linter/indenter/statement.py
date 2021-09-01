import re
JINJA_STATEMENT_TAG_NAMES = [
    ('for', 'else', 'endfor'),
    ('if', 'elif', 'else', 'endif'),
]

JINJA_INTERMEDIATE_TAG_NAMES = ["set", "include"]


class JinjaStatement:
    begin = None
    words = []

    def __init__(self, line):
        whitespaces = re.findall('\s*', line[0])

        self.begin = len(whitespaces[0])
        self.line = line[0]
        self.words = line[0].split()
        self.start_line_no = line[1]
        self.end_line_no = line[2]

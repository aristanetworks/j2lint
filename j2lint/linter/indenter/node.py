from j2lint.linter.indenter.statement import JinjaStatement, JINJA_STATEMENT_TAG_NAMES, JINJA_INTERMEDIATE_TAG_NAMES
from j2lint.linter.error import JinjaLinterError, JinjaBadIndentationError
from j2lint.utils import flatten, get_tuple, delimit_jinja_statement

BEGIN_TAGS = [item[0] for item in JINJA_STATEMENT_TAG_NAMES]
END_TAGS = [item[-1] for item in JINJA_STATEMENT_TAG_NAMES]
MIDDLE_TAGS = flatten([[i[1:-1] for i in JINJA_STATEMENT_TAG_NAMES]])

INDENT_SHIFT = 4
DEFAULT_WHITESPACES = 1

jinja_node_stack = []


class Node:
    statement = None
    tag = None
    node_start = 0
    node_end = 0
    children = []
    expected_indent = 0

    def create_node(self, line, line_no, indent_level=0):
        node = Node()
        statement = JinjaStatement(line)
        node.statement = statement
        node.tag = statement.words[0]
        node.node_start = line_no
        node.node_end = line_no
        node.expected_indent = indent_level
        node.parent = self
        return node

    def check_indent_level(self, result, node):
        actual = node.statement.begin
        expected = node.expected_indent + DEFAULT_WHITESPACES
        if actual != expected:
            result.append((node.statement.start_line_no,
                           delimit_jinja_statement(node.statement.line),
                           "Bad Indentation, expected %d, got %d" % (expected, actual)))
        return None

    def check_indentation(self, result, lines, line_no=0, indent_level=0):
        while line_no < len(lines):
            line = lines[line_no]
            node = self.create_node(line, line_no, indent_level)
            if node.tag in BEGIN_TAGS:
                jinja_node_stack.append(node)
                self.children.append(node)
                line_no = node.check_indentation(
                    result, lines, line_no + 1, indent_level + INDENT_SHIFT)
                self.check_indent_level(result, node)
                continue
            elif node.tag in END_TAGS:
                if ('end' + jinja_node_stack[-1].tag) == node.tag:
                    matchnode = jinja_node_stack.pop()
                    matchnode.node_end = line_no
                    node.node_end = line_no
                    node.expected_indent = matchnode.expected_indent
                    self.parent.children.append(node)
                    if matchnode == self:
                        line_no = line_no + 1
                        self.check_indent_level(result, node)
                        return line_no
                    raise JinjaLinterError("Tag is out of order" % (node.tag))
            elif node.tag in MIDDLE_TAGS:
                begin_tag_tuple = get_tuple(
                    JINJA_STATEMENT_TAG_NAMES, jinja_node_stack[-1].tag)
                if node.tag in begin_tag_tuple:
                    node.node_end = line_no
                    node.expected_indent = matchnode.expected_indent
                    self.parent.children.append(node)
                    line_no = line_no + 1
                    self.check_indent_level(result, node)
                    return line_no
                else:
                    raise JinjaLinterError(
                        "Unsupported tag %s found" % (node.tag))
            elif node.tag in JINJA_INTERMEDIATE_TAG_NAMES:
                self.children.append(node)
                line_no = line_no + 1
                self.check_indent_level(result, node)
                continue
            else:
                raise JinjaLinterError("Unsupported tag %s found" % (node.tag))

"""node.py - Class node for creating a parse tree for jinja statements and
             checking jinja statement indentation.
"""
from __future__ import annotations

from typing import NoReturn, Tuple

from j2lint.linter.error import JinjaLinterError
from j2lint.linter.indenter.statement import JINJA_STATEMENT_TAG_NAMES, JinjaStatement
from j2lint.logger import logger
from j2lint.utils import Statement, delimit_jinja_statement, flatten, get_tuple

BEGIN_TAGS = [item[0] for item in JINJA_STATEMENT_TAG_NAMES]
END_TAGS = [item[-1] for item in JINJA_STATEMENT_TAG_NAMES]
MIDDLE_TAGS = list(flatten([[i[1:-1] for i in JINJA_STATEMENT_TAG_NAMES]]))

INDENT_SHIFT = 4
DEFAULT_WHITESPACES = 1
JINJA_START_DELIMITERS = ["{%-", "{%+"]

jinja_node_stack: list[Node] = []
jinja_delimiter_stack: list[str] = []

# Using Tuple from typing for 3.8 support
NodeIndentationError = Tuple[int, str, str]


class Node:
    """Node class which represents a jinja file as a tree"""

    # pylint: disable=too-many-instance-attributes
    # Eight arguments is reasonable in this case
    def __init__(self) -> None:
        self.statement: JinjaStatement | None = None
        self.tag: str | None = None
        self.parent: Node = self
        self.node_start: int = 0
        self.node_end: int = 0
        self.children: list[Node] = []
        self.block_start_indent: int = 0
        self.expected_indent: int = 0

    # pylint: disable=fixme
    # TODO - This should be called create_child_node
    def create_node(self, line: Statement, line_no: int, indent_level: int = 0) -> Node:
        """Initializes a Node class object

        Args:
            line (Statement): Parsed line of the template using get_jinja_statement
            line_no (int): line number
            indent_level (int, optional): expected indentation level. Defaults to 0.

        Returns:
            Node: new Node class object
        """
        node = Node()
        statement = JinjaStatement(line)
        node.statement = statement
        node.tag = statement.words[0]
        node.node_start = line_no
        node.node_end = line_no
        node.expected_indent = indent_level
        node.parent = self
        return node

    @staticmethod
    def create_indentation_error(
        node: Node, message: str
    ) -> NodeIndentationError | None:
        """Creates indentation error tuple

        Args:
            node (Node): Node class object to create error for
            message (string): error message for the line

        Returns:
            tuple: tuple representing the indentation error
        """
        if node.statement is None:
            return None

        return (
            node.statement.start_line_no,
            delimit_jinja_statement(
                node.statement.line,
                node.statement.start_delimiter,
                node.statement.end_delimiter,
            ),
            message,
        )

    def check_indent_level(
        self, result: list[NodeIndentationError], node: Node
    ) -> None:
        """check if the actual and expected indent level for a line match

        Args:
            result (list): list of tuples of indentation errors
            node (Node): Node object for which to check the level is correct
        """
        if node.statement is None:
            return
        actual = node.statement.begin
        if (
            jinja_node_stack
            and jinja_node_stack[0].statement is not None
            and jinja_node_stack[0].statement.start_delimiter in JINJA_START_DELIMITERS
        ):
            self.block_start_indent = 1
        elif (
            node.expected_indent == 0
            and node.statement.start_delimiter in JINJA_START_DELIMITERS
        ):
            self.block_start_indent = 1
        else:
            self.block_start_indent = 0

        if node.statement.start_delimiter in JINJA_START_DELIMITERS:
            expected = node.expected_indent + self.block_start_indent
        else:
            expected = (
                node.expected_indent + DEFAULT_WHITESPACES + self.block_start_indent
            )
        if actual != expected:
            message = f"Bad Indentation, expected {expected}, got {actual}"
            if (error := self.create_indentation_error(node, message)) is not None:
                result.append(error)
                logger.debug(error)

    def _assert_not_none(self, current_line_no: int, new_line_no: int | None) -> int:
        """
        Helper function to verify that the new_line_no is not None
        TODO: Probably should never return None and instead raise in check_indentation
        """
        if new_line_no is None:
            raise JinjaLinterError(
                "Recursive check_indentation returned None for an opening tag "
                f"line {current_line_no} - missing closing tag",
            )
        return new_line_no

    # pylint: disable=inconsistent-return-statements,fixme
    # TODO - newer version of pylint (2.17.0) catches some error here
    #        address in refactoring
    def check_indentation(
        self,
        result: list[NodeIndentationError],
        lines: list[Statement],
        line_no: int = 0,
        indent_level: int = 0,
    ) -> int | None:
        """Checks indentation for a list of lines
        Updates the 'result' list argument with indentation errors

        Args:
            result (list): list of indentation error tuples
            lines (list): lines which are to be checked for indentation
            line_no (int, optional):  the current lines number being evaluated.
                                      Defaults to 0.
            indent_level (int, optional): the expected indent level for the
                                          current line. Defaults to 0.

        Raises:
            JinjaLinterError: Raises error if the text file has jinja tags
                              which are not supported by this indenter
            ValueError: Raised when no begin_tag_tuple can be found in a node in the stack

        Returns:
            line_no (int) or None
        """

        def _append_error_to_result_and_raise(message: str) -> NoReturn:
            """
            Helper function to append error to result and raise a JinjaLinterError
            """
            if (error := self.create_indentation_error(node, message)) is not None:
                result.append(error)
            raise JinjaLinterError(message)

        def _handle_begin_tag(node: Node, line_no: int) -> int:
            jinja_node_stack.append(node)
            self.children.append(node)
            line_no = self._assert_not_none(
                line_no,
                node.check_indentation(
                    result, lines, line_no + 1, indent_level + INDENT_SHIFT
                ),
            )

            self.check_indent_level(result, node)
            return line_no

        def _handle_middle_tag(node: Node, line_no: int) -> int:
            matchnode = jinja_node_stack[-1]
            node.node_end = line_no
            node.expected_indent = matchnode.expected_indent
            indent_level = node.expected_indent
            matchnode.parent.children.append(node)
            node.parent = matchnode.parent

            line_no = self._assert_not_none(
                line_no,
                node.check_indentation(
                    result, lines, line_no + 1, indent_level + INDENT_SHIFT
                ),
            )

            self.check_indent_level(result, node)
            return line_no

        def _handle_end_tag(node: Node, line_no: int) -> int:  # type: ignore
            if f"end{jinja_node_stack[-1].tag}" == node.tag:
                if jinja_node_stack[-1] != self:
                    return line_no
                matchnode = jinja_node_stack[-1]
                matchnode.node_end = line_no
                node.node_end = line_no
                node.expected_indent = matchnode.expected_indent
                self.parent.children.append(node)  # type: ignore
                if matchnode == self:
                    line_no += 1
                    self.check_indent_level(result, node)
                    jinja_node_stack.pop()
                    return line_no
            # End Tag not matching the begin tag - raise an error
            message = f"Line {line_no} - Tag is out of order '{node.tag}'"
            _append_error_to_result_and_raise(message)
            # Never reached
            return line_no

        while line_no < len(lines):
            line = lines[line_no]
            node = self.create_node(line, line_no, indent_level)
            if node.tag in BEGIN_TAGS:
                line_no = _handle_begin_tag(node, line_no)
                continue

            if node.tag in END_TAGS:
                return _handle_end_tag(node, line_no)

            if node.tag in MIDDLE_TAGS:
                begin_tag_tuple = get_tuple(
                    JINJA_STATEMENT_TAG_NAMES, jinja_node_stack[-1].tag
                )
                if begin_tag_tuple is None:
                    _append_error_to_result_and_raise(
                        f"Node {jinja_node_stack[-1]} should have been a begin_tag"
                    )

                if node.tag in begin_tag_tuple:  # type: ignore
                    if jinja_node_stack[-1] != self:
                        del node
                        return line_no
                    line_no = _handle_middle_tag(node, line_no)
                    continue

                message = f"Unsupported tag '{node.tag}' found"
                _append_error_to_result_and_raise(message)

            self.children.append(node)
            line_no = line_no + 1
            self.check_indent_level(result, node)

        return None

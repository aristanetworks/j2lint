# Copyright (c) 2021-2026 Arista Networks, Inc.
# Use of this source code is governed by the MIT license
# that can be found in the LICENSE file.
"""Tests for j2lint.linter.node.py."""

from __future__ import annotations

import pytest

from j2lint.linter.indenter.node import Node, NodeIndentationError, jinja_node_stack


class TestNode:
    """Test j2lint.linter.node.Node."""

    @pytest.mark.skip("No need to test this")
    def test_create_node(self) -> None:
        """N/A."""
        # TODO: why is it not an __init__ method???

    def test_create_indentation_error(self) -> None:
        """Test the Node.create_indentation_error method."""
        line = (
            " if switch.platform_settings.tcam_profile is arista.avd.defined ",
            2,
            2,
            "{%",
            "%}",
        )
        root = Node()
        node = root.create_node(line, 2)

        indentation_error = node.create_indentation_error(node, "test")
        assert indentation_error == (
            2,
            "{% if switch.platform_settings.tcam_profile is arista.avd.defined %}",
            "test",
        )

    def test_check_indentation_returns_to_begin_tag_after_middle_tag(self) -> None:
        """Test that a middle tag returns parsing to the matching begin tag."""
        lines = [
            (" if enabled ", 1, 1, "{%", "%}"),
            (" else ", 2, 2, "{%", "%}"),
            (" endif ", 3, 3, "{%", "%}"),
        ]
        result: list[NodeIndentationError] = []
        jinja_node_stack.clear()

        try:
            assert Node().check_indentation(result, lines, 0) is None
            assert not result
            assert not jinja_node_stack
        finally:
            jinja_node_stack.clear()

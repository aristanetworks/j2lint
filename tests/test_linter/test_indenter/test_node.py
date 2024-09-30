# Copyright (c) 2021-2024 Arista Networks, Inc.
# Use of this source code is governed by the MIT license
# that can be found in the LICENSE file.
"""Tests for j2lint.linter.node.py"""

import pytest

from j2lint.linter.indenter.node import Node


class TestNode:
    @pytest.mark.skip("No need to test this")
    def test_create_node(self):
        """ """
        # TODO - why is it not an __init__ method???

    def test_create_indentation_error(self):
        """Test the Node.create_indentation_error method"""
        line = (
            " if switch.platform_settings.tcam_profile is arista.avd.defined ",
            2,
            2,
            "{%",
            "%}",
        )
        root = Node()
        node = root.create_node(line, 2)
        print(node.statement)

        indentation_error = node.create_indentation_error(node, "test")
        print(type(indentation_error))
        assert indentation_error == (
            2,
            "{% if switch.platform_settings.tcam_profile is arista.avd.defined %}",
            "test",
        )

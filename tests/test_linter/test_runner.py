# Copyright (c) 2021-2024 Arista Networks, Inc.
# Use of this source code is governed by the MIT license
# that can be found in the LICENSE file.
"""Tests for j2lint.linter.runner.py."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest import mock

import pytest

if TYPE_CHECKING:
    from pathlib import Path

    from j2lint.linter.runner import Runner


class TestRunner:
    """Test j2lint.linter.runner.Runner."""

    @pytest.mark.parametrize(
        ("file_path", "checked_files", "expected"),
        [
            ("test.j2", [], False),
            ("test.j2", ["other.j2"], False),
            ("test.j2", ["test.j2"], True),
        ],
    )
    def test_is_already_checked(self, test_runner: Runner, file_path: Path, checked_files: list[Path], *, expected: bool) -> None:
        """Test Runner.is_already_checked method."""
        test_runner.checked_files = checked_files
        assert test_runner.is_already_checked(file_path) == expected

    # TODO: refactor the code and augment the tests..
    #       today if we give multiple files to a runner
    #       only the errors, warnings of the last one will
    #       be kept..
    @pytest.mark.parametrize(
        "runner_files",
        [
            ([]),
            (["test.j2"]),
            (["test.j2", "test2.j2"]),
            (["test.txt"]),
        ],
    )
    def test_run(self, test_runner: Runner, runner_files: list[Path]) -> None:
        """Test Runner.run method.

        For now only testing with one input file given that this
        is how the package is working.

        This test is "bad" for now.
        """
        test_runner.files = runner_files
        # Fake return
        with mock.patch("j2lint.linter.collection.RulesCollection.run") as patched_collection_run:
            patched_collection_run.return_value = ([], [])
            result = test_runner.run()

            assert len(runner_files) == patched_collection_run.call_count
            assert result == ([], [])

            for file in test_runner.files:
                patched_collection_run.assert_any_call(file)
                assert file in test_runner.checked_files

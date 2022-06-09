"""
Tests for j2lint.linter.runner.py
"""
import pytest

from j2lint.utils import get_file_type
from j2lint.linter.runner import Runner


@pytest.fixture
def runner(mock_collection):
    return Runner(mock_collection, "test.j2", checked_files=None)


class TestRunner:
    @pytest.mark.parametrize(
        "file_path, checked_files, expected",
        [
            ("test.j2", set(), False),
            ("test.j2", ("other.j2"), False),
            ("test.j2", ("test.j2"), True),
        ],
    )
    def test_is_already_checked(self, runner, file_path, checked_files, expected):
        """
        test Runner.is_already_checked method
        """
        runner.checked_files = checked_files
        assert runner.is_already_checked(file_path) == expected

    # FIXME: refactor the code and augment the tests..
    #        today if we give multiple files to a runner
    #        only the errors, warnings of the last one will
    #        be kept..
    @pytest.mark.parametrize(
        "runner_files",
        [
            ([]),
            (["test.j2"]),
            (["test.j2", "test2.j2"]),
        ],
    )
    def test_run(self, runner, runner_files):
        """
        test Runner.run method

        For now only testing with one input file given that this
        is how the package is working.

        This test is "bad" for now.
        """
        runner.files = set()
        for file in runner_files:
            runner.files.add((file, get_file_type(file)))

        # Fake return
        runner.collection.run.return_value = ([], [])
        result = runner.run()

        assert len(runner_files) == runner.collection.run.call_count
        assert result == ([], [])

        for file in runner.files:
            runner.collection.run.assert_any_call({"path": file[0], "type": file[1]})
            assert file[0] in runner.checked_files

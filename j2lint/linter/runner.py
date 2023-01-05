"""runner.py - Class to run the rules collection for all the files.
"""
from __future__ import annotations

from j2lint.logger import logger
from j2lint.utils import get_file_type

from .collection import RulesCollection
from .error import LinterError


class Runner:
    """Class to run the rules collection for all the files

    TODO: refactor - with this code it seems that files will always
          be a set of 1 file - indeed, a different Runner is created
          for each file in cli.py
    """

    def __init__(
        self,
        collection: RulesCollection,
        file_name: str,
        checked_files: list[str],
    ) -> None:
        self.collection = collection
        self.files: set[tuple[str, str]] = set()
        if (file_type := get_file_type(file_name)) is not None:
            self.files.add((file_name, file_type))

        self.checked_files = checked_files

    def is_already_checked(self, file_path: str) -> bool:
        """Returns true if the file is already checked once

        Args:
            file_path (string): file path

        Returns:
            bool: True if file is already checked once
        """
        return file_path in self.checked_files

    def run(self) -> tuple[list[LinterError], list[LinterError]]:
        """Runs the lint rules collection on all the files

        Returns:
            tuple(list, list): a tuple containing the list of linting errors
                               and the list of linting warnings found
        TODO - refactor this - it is quite weird to do the conversion
                               from tuple to dict here
                               maybe simply init with the dict
        """
        file_dicts: list[dict[str, str]] = []
        for index, file in enumerate(self.files):
            logger.debug("Running linting rules for %s", file)
            file_path = file[0]
            file_type = file[1]
            file_dict = {"path": file_path, "type": file_type}
            # pylint: disable = fixme
            # FIXME - as of now it seems that both next tests
            #         will never occurs as self.files is always
            #         a single file.
            # Skip already checked files
            if self.is_already_checked(file_path):
                continue
            # Skip duplicate files
            if file_dict in file_dicts[:index]:
                continue
            file_dicts.append(file_dict)

        errors: list[LinterError] = []
        warnings: list[LinterError] = []
        # pylint: disable = fixme
        # FIXME - if there are multiple files, errors and warnings are overwritten..
        for file_dict in file_dicts:
            errors, warnings = self.collection.run(file_dict)

        # Update list of checked files
        self.checked_files.extend([file_dict["path"] for file_dict in file_dicts])

        return errors, warnings

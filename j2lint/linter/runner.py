# Copyright (c) 2021-2025 Arista Networks, Inc.
# Use of this source code is governed by the MIT license
# that can be found in the LICENSE file.
"""runner.py - Class to run the rules collection for all the files."""

from __future__ import annotations

from typing import TYPE_CHECKING

from j2lint.logger import logger

if TYPE_CHECKING:
    from pathlib import Path

    from .collection import RulesCollection
    from .error import LinterError


class Runner:
    """Class to run the rules collection for all the files.

    TODO: refactor - with this code it seems that files will always
          be a set of 1 file - indeed, a different Runner is created
          for each file in cli.py
    """

    def __init__(self, collection: RulesCollection, file_name: Path, checked_files: list[Path]) -> None:
        self.collection = collection
        self.files: set[Path] = {file_name}
        self.checked_files = checked_files

    def is_already_checked(self, file_path: Path) -> bool:
        """Return True if the file is already checked once.

        Parameters
        ----------
        file_path
            File path

        Returns
        -------
        bool
            True if file is already checked once
        """
        return file_path in self.checked_files

    def run(self) -> tuple[list[LinterError], list[LinterError]]:
        """Run the lint rules collection on all the files.

        Returns
        -------
        tuple[list, list]
            A tuple containing the list of linting errors and the list of linting warnings found.

        TODO: refactor this - it is quite weird to do the conversion from tuple to dict here maybe simply init with the dict
        """
        files: list[Path] = []
        for index, file in enumerate(self.files):
            # TODO: as of now it seems that both next tests will never occurs as self.files is always a single file.
            # Skip already checked files
            if self.is_already_checked(file):
                continue
            # Skip duplicate files
            if file in files[:index]:
                continue
            files.append(file)

        errors: list[LinterError] = []
        warnings: list[LinterError] = []
        # TODO: if there are multiple files, errors and warnings are overwritten.. fortunately there is only one file currently
        for file in files:
            logger.debug("Running linting rules for %s", file)
            errors, warnings = self.collection.run(file)

        # Update list of checked files
        self.checked_files.extend(files)

        return errors, warnings

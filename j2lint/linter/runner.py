"""runner.py - Class to run the rules collection for all the files.
"""

from j2lint.utils import get_file_type
from j2lint.logger import logger


class Runner:
    """Class to run the rules collection for all the files

    TODO: refactor - with this code it seems that files will always
          be a set of 1 file - indeed, a different Runner is created
          for each file in cli.py
    """

    def __init__(self, collection, file_name, checked_files=None):
        self.collection = collection
        self.files = set()
        self.files.add((file_name, get_file_type(file_name)))

        # Set the checked files
        if checked_files is None:
            checked_files = set()
        self.checked_files = checked_files

    def is_already_checked(self, file_path):
        """Returns true if the file is already checked once

        Args:
            file_path (string): file path

        Returns:
            boolean: True if file is already checked once
        """
        return file_path in self.checked_files

    def run(self):
        """Runs the lint rules collection on all the files

        Returns:
            list: list of LinterError objects
        """
        files = []
        for index, file in enumerate(self.files):
            logger.debug("Running linting rules for %s", file)
            file_path = file[0]
            file_type = file[1]
            file_dict = {'path': file_path, 'type': file_type}
            # pylint: disable = fixme
            # FIXME - as of now it seems that both next tests
            #         will never occurs as self.files is always
            #         a single file.
            # Skip already checked files
            if self.is_already_checked(file_path):
                continue
            # Skip duplicate files
            if file_dict in files[:index]:
                continue
            files.append(file_dict)

        errors = []
        warnings = []
        # pylint: disable = fixme
        # FIXME - if there are multiple files, errors and warnings are overwritten..
        for file in files:
            errors, warnings = self.collection.run(file)

        # Update list of checked files
        self.checked_files.update([file_dict['path'] for file_dict in files])

        return errors, warnings

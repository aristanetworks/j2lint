import os

from j2lint.utils import get_file_type
from j2lint.logger import logger


class Runner:
    def __init__(self, collection, file_name, config, checked_files=None):
        self.collection = collection
        self.files = set()
        self.files.add((file_name, get_file_type(file_name)))

        # Set the checked files
        if checked_files is None:
            checked_files = set()
        self.checked_files = checked_files

    def is_already_checked(self, file_path):
        return file_path in self.checked_files

    def run(self):
        """Run the linting rules collection against all the files"""
        files = []
        for index, file in enumerate(self.files):
            logger.debug("Running linting rules for {}".format(file))
            file_path = file[0]
            file_type = file[1]
            file_dict = {'path': file_path, 'type': file_type}
            # Skip already checked files
            if self.is_already_checked(file_path):
                continue
            # Skip duplicates
            if file_dict in files[:index]:
                continue
            files.append(file_dict)

        errors = []
        for file in files:
            errors.extend(self.collection.run(file))

        # Update list of checked files
        self.checked_files.update([file_dict['path'] for file_dict in files])

        logger.info("Linting errors found {}".format(errors))
        return errors

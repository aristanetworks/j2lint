import re

from j2lint.utils import is_valid_file_type, LANGUAGE_JINJA
from j2lint.linter.error import LinterError
from j2lint.logger import logger


class Rule:
    id = None
    description = None
    match = None
    matchtext = None
    ignore = False

    def __repr__(self):
        return self.id + ": " + self.description

    def is_valid_language(self, file):
        """Check if the file has the expected language"""
        if is_valid_file_type(file["path"]):
            return True
        return False

    def matchlines(self, file, text):
        """Check each line in the given file to check if the current rule matches"""
        errors = []

        if not self.match:
            logger.debug("Match line rule does not exist for {}".format(
                __class__.__name__))
            return errors

        if not self.is_valid_language(file):
            logger.debug(
                "Skipping file {}. Linter does not support linting this file type".format(file))
            return errors

        for (index, line) in enumerate(text.split("\n")):
            if line.lstrip().startswith('#'):
                continue

            result = self.match(file, line)
            if not result:
                continue
            errors.append(LinterError(index+1, line, file['path'], self))
        return errors

    def matchfulltext(self, file, text):
        errors = []

        if not self.matchtext:
            logger.debug("Match text rule does not exist for {}".format(
                __class__.__name__))
            return errors

        if not self.is_valid_language(file):
            logger.debug(
                "Skipping file {}. Linter does not support linting this file type".format(file))
            return errors

        results = self.matchtext(file, text)

        for line, section, message in results:
            errors.append(LinterError(
                line, section, file['path'], self, message))

        return errors

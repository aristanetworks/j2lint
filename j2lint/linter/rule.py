"""rule.py - Base class for all the lint rules with functions for mathching
             line and text based rule.
"""
import re

from j2lint.utils import is_valid_file_type, LANGUAGE_JINJA
from j2lint.linter.error import LinterError
from j2lint.logger import logger


class Rule:
    """Rule class which acts as a base class for rules with regex match
       functions.
    """
    id = None
    description = None
    check = None
    checktext = None
    ignore = False
    warn = []

    def __repr__(self):
        return self.id + ": " + self.description

    def is_valid_language(self, file):
        """Check if the file is a valid Jinja file

        Args:
            file (string): file path

        Returns:
            boolean: True if file extension is correct
        """

        if is_valid_file_type(file["path"]):
            return True
        return False

    def checklines(self, file, text):
        """Checks each line of file against the error regex

        Args:
            file (string): file path of the file to be checked
            text (string): file text of the same file

        Returns:
            list: list of issues in the given file
        """
        errors = []

        if not self.check:
            logger.debug("Check line rule does not exist for {}".format(
                __class__.__name__))
            return errors

        if not self.is_valid_language(file):
            logger.debug(
                "Skipping file {}. Linter does not support linting this file type".format(file))
            return errors

        for (index, line) in enumerate(text.split("\n")):
            if line.lstrip().startswith('#'):
                continue

            result = self.check(file, line)
            if not result:
                continue
            errors.append(LinterError(index+1, line, file['path'], self))
        return errors

    def checkfulltext(self, file, text):
        """Checks the entire file text against a lint rule

        Args:
            file (string): file path of the file to be checked
            text (string): file text of the same file

        Returns:
            list: list of issues in the given file
        """
        errors = []

        if not self.checktext:
            logger.debug("Check text rule does not exist for {}".format(
                __class__.__name__))
            return errors

        if not self.is_valid_language(file):
            logger.debug(
                "Skipping file {}. Linter does not support linting this file type".format(file))
            return errors

        results = self.checktext(file, text)

        for line, section, message in results:
            errors.append(LinterError(
                line, section, file['path'], self, message))

        return errors

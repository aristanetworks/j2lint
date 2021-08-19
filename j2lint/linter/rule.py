import re

from j2lint.utils import is_valid_file_type
from j2lint.linter.linterror import LintError
from j2lint.utils import LANGUAGE_JINJA


class Rule:
    id = None
    description = None
    match = None
    matchtext = None

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
            return errors

        if not self.is_valid_language(file):
            return errors

        for (index, line) in enumerate(text.split("\n")):
            if line.lstrip().startswith('#'):
                continue

            result = self.match(file, line)
            if not result:
                continue
            errors.append(LintError(index+1, line, file['path'], self))
        return errors

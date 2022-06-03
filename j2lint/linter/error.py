"""error.py - Error classes to format the lint errors.
"""
import json
from j2lint.settings import settings
from j2lint.logger import logger

# pylint: disable=too-few-public-methods,too-many-arguments


class LinterError:
    """Class for lint errors.
    """

    def __init__(self, line_number, line, filename, rule, message=None):
        self.line_number = line_number
        self.line = line
        self.filename = filename
        self.rule = rule
        self.message = rule.description if not message else message

    def __repr__(self, verbose=False):
        if settings.output == "json":
            error = json.dumps({"id": self.rule.id,
                                "message": self.message,
                                "filename": self.filename,
                                "line_number": self.line_number,
                                "line": self.line,
                                "severity": self.rule.severity
                                })
        else:
            if not settings.verbose:
                format_str = "{2}:{3} {5} ({6})"
            else:
                format_str = ("Linting rule: {0}\nRule description: "
                            "{1}\nError line: {2}:{3} {4}\nError message: {5}\n")
            error = format_str.format(self.rule.id, self.rule.description,
                                     self.filename, self.line_number, self.line,
                                     self.message, self.rule.short_description)
        logger.error(error)
        return error


class JinjaLinterError(Exception):
    """ Jinja Linter Error"""

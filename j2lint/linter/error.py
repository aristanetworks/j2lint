"""error.py - Error classes to format the lint errors.
"""
from j2lint.settings import settings
from j2lint.logger import logger
import json


class LinterError:
    """Class for lint errors.
    """

    def __init__(self, linenumber, line, filename, rule, message=None):
        self.linenumber = linenumber
        self.line = line
        self.filename = filename
        self.rule = rule
        self.message = rule.description if not message else message

    def __repr__(self, verbose=False):
        if settings.output == "json":
            error = json.dumps({"id": self.rule.id,
                                "message": self.message,
                                "filename": self.filename,
                                "linenumber": self.linenumber,
                                "line": self.line,
                                "severity": self.rule.severity
                                })
        else:
            if not settings.verbose:
                formatstr = "{2}:{3} {5} ({6})"
            else:
                formatstr = "Linting rule: {0}\nRule description: {1}\nError line: {2}:{3} {4}\nError message: {5}\n"
            error = formatstr.format(self.rule.id, self.rule.description,
                                     self.filename, self.linenumber, self.line, self.message, self.rule.short_description)
        logger.error(error)
        return error


class JinjaBadIndentationError(Exception):
    pass


class JinjaLinterError(Exception):
    pass

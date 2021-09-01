class LinterError:
    def __init__(self, linenumber, line, filename, rule, message=None):
        self.linenumber = linenumber
        self.line = line
        self.filename = filename
        self.rule = rule
        self.message = rule.description if not message else message

    def __repr__(self):
        formatstr = u"Rule: {0}\nRule Description: {1}\nLinter Error found in: {2}:{3} {4}\nError message: {5}\n"
        return formatstr.format(self.rule.id, self.rule.description,
                                self.filename, self.linenumber, self.line, self.message)


class JinjaBadIndentationError(Exception):
    pass


class JinjaLinterError(Exception):
    pass

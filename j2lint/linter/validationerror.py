class ValidationError:
    def __init__(self, linenumber, line, filename, rule, message=None):
        self.linenumber = linenumber
        self.line = line
        self.filename = filename
        self.rule = rule
        self.message = rule.description if not message else message

    def __repr__(self):
        formatstr = u"Rule: {0}\nRule Description: {1}\nValidation Error found in: {2}:{3} {4}\n"
        return formatstr.format(self.rule.id, self.message,
                                self.filename, self.linenumber, self.line)

class LintError:
    def __init__(self, linenumber, line, filename, rule):
        self.linenumber = linenumber
        self.line = line
        self.filename = filename
        self.rule = rule
        self.message = rule.description

    def __repr__(self):
        formatstr = u"Rule {0}: {1}. Problem found in {2}:{3} {4}."
        return formatstr.format(self.rule.id, self.message,
                                self.filename, self.linenumber, self.line)

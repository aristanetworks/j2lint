from collections import defaultdict
import os
import sys

from j2lint.utils import load_plugins
from j2lint.logger import logger


class RulesCollection:
    def __init__(self, verbose=False):
        self.rules = []
        self.verbose = verbose

    def __iter__(self):
        return iter(self.rules)

    def __len__(self):
        return len(self.rules)

    def extend(self, more):
        self.rules.extend(more)

    def run(self, file_dict):
        """Run the linting rule checks for the specified file"""
        text = ""
        errors = []

        try:
            with open(file_dict['path'], mode='r') as f:
                text = f.read()
        except IOError as e:
            print("WARNING: Couldn't open %s - %s" %
                  (file_dict['path'], e.strerror), file=sys.stderr)
            return matches

        for rule in self.rules:
            logger.debug("Running linting rule {} on file {}".format(
                rule, file_dict['path']))
            errors.extend(rule.matchlines(file_dict, text))
            errors.extend(rule.matchfulltext(file_dict, text))

        return errors

    def __repr__(self):
        return "\n".join([repr(rule)
                          for rule in sorted(self.rules, key=lambda x: x.id)])

    @classmethod
    def create_from_directory(clazz, rulesdir):
        """Creates a collection from all rule modules"""
        result = clazz()
        result.rules = load_plugins(os.path.expanduser(rulesdir))
        logger.info(
            "Created collection from rules directory {}".format(rulesdir))
        return result

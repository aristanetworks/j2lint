"""collection.py - Class to create a collection of linting rules.
"""
from collections import defaultdict
import os
import sys

from j2lint.utils import load_plugins, is_rule_disabled
from j2lint.logger import logger


class RulesCollection:
    """RulesCollection class which checks the linting rules against a file.
    """

    def __init__(self, verbose=False):
        self.rules = []
        self.verbose = verbose

    def __iter__(self):
        return iter(self.rules)

    def __len__(self):
        return len(self.rules)

    def extend(self, more):
        """Extends list of rules

        Args:
            more (list): list of rules classes
        """
        self.rules.extend(more)

    def run(self, file_dict):
        """Runs the linting rules for given file

        Args:
            file_dict (dict): file path and file type

        Returns:
            list: list of linting errors found
        """
        text = ""
        errors = []
        warnings = []

        try:
            with open(file_dict['path'], mode='r') as f:
                text = f.read()
        except IOError as e:
            print("WARNING: Couldn't open %s - %s" %
                  (file_dict['path'], e.strerror), file=sys.stderr)
            return errors

        for rule in self.rules:
            if rule.ignore:
                logger.debug("Ignoring rule {}:{} for file {}".format(
                    rule.id, rule.short_description, file_dict['path']))
                continue
            if is_rule_disabled(text, rule):
                logger.debug("Skipping linting rule {} on file {}".format(
                    rule, file_dict['path']))
                continue
            logger.debug("Running linting rule {} on file {}".format(
                rule, file_dict['path']))
            if rule in rule.warn:
                warnings.extend(rule.checklines(file_dict, text))
                warnings.extend(rule.checkfulltext(file_dict, text))
            else:
                errors.extend(rule.checklines(file_dict, text))
                errors.extend(rule.checkfulltext(file_dict, text))

        return errors, warnings

    def __repr__(self):
        return "\n".join([repr(rule)
                          for rule in sorted(self.rules, key=lambda x: x.id)])

    @classmethod
    def create_from_directory(clazz, rules_dir, ignore_rules, warn_rules):
        """Creates a collection from all rule modules

        Args:
            clazz (Object): object of a rule class
            rules_dir (string): rules directory
            ignore_rules (list): list of rule descriptions to ignore

        Returns:
            list: a collection of rule objects
        """
        result = clazz()
        result.rules = load_plugins(os.path.expanduser(rules_dir))
        for rule in result.rules:
            if (rule.short_description in ignore_rules) or (rule.id in ignore_rules):
                rule.ignore = True
            if (rule.short_description in warn_rules) or (rule.id in warn_rules):
                rule.warn.append(rule)
        logger.info(
            "Created collection from rules directory {}".format(rules_dir))
        return result

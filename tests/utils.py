"""
utils.py - functions to assist with tests
"""
from contextlib import contextmanager
import pytest


@contextmanager
def does_not_raise():
    yield

import logging
from logging.handlers import RotatingFileHandler
from logging import handlers
import sys

logger = logging.getLogger('')
logger.setLevel(logging.INFO)
format = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s")

ch = logging.StreamHandler(sys.stdout)
ch.setFormatter(format)
logger.addHandler(ch)

fh = handlers.RotatingFileHandler(
    'jinja2-linter.log', maxBytes=(1048576*5), backupCount=4)
fh.setFormatter(format)
logger.addHandler(fh)

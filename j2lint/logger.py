import logging
from logging.handlers import RotatingFileHandler
from logging import handlers

logger = logging.getLogger('')
logger.setLevel(logging.INFO)
log_format = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s")

fh = handlers.RotatingFileHandler(
    'jinja2-linter.log', maxBytes=(1048576*5), backupCount=4)
fh.setFormatter(log_format)
logger.addHandler(fh)

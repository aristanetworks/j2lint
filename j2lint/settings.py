"""settings.py - Settings class for jinja2 linter.
"""
# pylint: disable=R0903

class Settings:
    """Class for jinja2 linter settings.
    """
    verbose = False
    log_level = "info"
    output = "text"


settings = Settings()

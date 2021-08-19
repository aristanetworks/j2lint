import glob
import importlib.util
import os

LANGUAGE_JINJA = "jinja"


def load_plugins(directory):
    """ Loads and executes all the Rule modules from the specified directory """
    result = []
    fh = None

    for pluginfile in glob.glob(os.path.join(directory, '[A-Za-z]*.py')):
        pluginname = os.path.basename(pluginfile.replace('.py', ''))
        try:
            spec = importlib.util.spec_from_file_location(
                pluginname, pluginfile)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            obj = getattr(module, pluginname)()
            result.append(obj)
        finally:
            if fh:
                fh.close()
    return result


def is_valid_file_type(file_name):
    """ Checks if the file is a valid Jinja file """
    extension = os.path.splitext(file_name)[1].lower()
    if extension in [".jinja", ".jinja2", ".j2"]:
        return True
    return False


def get_file_type(file_name):
    """ Returns file type as Jinja or None """
    if is_valid_file_type(file_name):
        return LANGUAGE_JINJA
    return None

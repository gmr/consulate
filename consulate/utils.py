"""
Misc utility functions and constants

"""
import sys

PYTHON3 = True if sys.version_info > (3, 0, 0) else False


def is_string(value):
    """Python 2 & 3 safe way to check if a value is either an instance of str
    or unicode.

    :param mixed value: The value to evaluate
    :rtype: bool

    """
    checks = [isinstance(value, str)]
    if not PYTHON3:
        checks.append(isinstance(value, unicode))
    return any(checks)

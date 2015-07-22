"""
Misc utility functions and constants

"""
import sys
try:
    from urllib.parse import quote
except ImportError:
    from urllib import quote

PYTHON3 = True if sys.version_info > (3, 0, 0) else False


def is_string(value):
    """Python 2 & 3 safe way to check if a value is either an instance of str
    or unicode.

    :param mixed value: The value to evaluate
    :rtype: bool

    """
    checks = [isinstance(value, t) for t in [bytes, str]]
    if not PYTHON3:
        checks.append(isinstance(value, unicode))
    return any(checks)


def maybe_encode(value):
    """If the value passed in is a str, encode it as UTF-8 bytes for Python 3

    :param str|bytes value: The value to maybe encode
    :rtype: bytes

    """
    try:
        return value.encode('utf-8')
    except AttributeError:
        return value

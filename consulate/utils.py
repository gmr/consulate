# coding=utf-8
"""
Misc utility functions and constants

"""
import re
import sys
try:  # pylint: disable=import-error
    from urllib.parse import quote
except ImportError:
    from urllib import quote

try:  # pylint: disable=import-error
    from urllib import parse as _urlparse
except ImportError:
    import urlparse as _urlparse


from consulate import exceptions

DURATION_PATTERN = re.compile(r'^(?:(?:-|)(?:\d+|\d+\.\d+)(?:µs|ms|s|m|h))+$')
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


def _response_error(response):
    """Return the decoded response error or status code if no content exists.

    :param requests.response response: The HTTP response
    :rtype: str

    """
    return (response.body.decode('utf-8')
            if hasattr(response, 'body') and response.body
            else str(response.status_code))


def response_ok(response, raise_on_404=False):
    """Evaluate the HTTP response and raise the appropriate exception if
    required.

    :param requests.response response: The HTTP response
    :param bool raise_on_404: Raise an exception on 404 error
    :rtype: bool
    :raises: consulate.exceptions.ConsulateException

    """
    if response.status_code == 200:
        return True
    elif response.status_code == 400:
        raise exceptions.ClientError(_response_error(response))
    elif response.status_code == 401:
        raise exceptions.ACLDisabled(_response_error(response))
    elif response.status_code == 403:
        raise exceptions.Forbidden(_response_error(response))
    elif response.status_code == 404 and raise_on_404:
        raise exceptions.NotFound(_response_error(response))
    elif response.status_code == 500:
        raise exceptions.ServerError(_response_error(response))
    return False


def validate_go_interval(value, _model=None):
    """Validate the value passed in returning :data:`True` if it is a Go
    Duration value.

    :param str value: The string to check
    :param consulate.models.base.Model _model: Optional model passed in
    :rtype: bool

    """
    return DURATION_PATTERN.match(value) is not None


def validate_url(value, _model=None):
    """Validate that the value passed in is a URL, returning :data:`True` if
    it is.

    :param str value: The string to check
    :param consulate.models.base.Model _model: Optional model passed in
    :rtype: bool

    """
    parsed = _urlparse.urlparse(value)
    return parsed.scheme and parsed.netloc

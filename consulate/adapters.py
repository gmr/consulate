# coding=utf-8
"""
HTTP Client Library Adapters

"""
import json
import logging
import socket

import requests
import requests.exceptions
try:
    import requests_unixsocket
except ImportError:  # pragma: no cover
    requests_unixsocket = None

from consulate import api, exceptions, utils

LOGGER = logging.getLogger(__name__)

CONTENT_FORM = 'application/x-www-form-urlencoded; charset=utf-8'
CONTENT_JSON = 'application/json; charset=utf-8'


def prepare_data(fun):
    """Decorator for transforming the data being submitted to Consul

    :param function fun: The decorated function

    """

    def inner(*args, **kwargs):
        """Inner wrapper function for the decorator

        :param list args: positional arguments
        :param dict kwargs: keyword arguments

        """
        if kwargs.get('data'):
            if not utils.is_string(kwargs.get('data')):
                kwargs['data'] = json.dumps(kwargs['data'])
        elif len(args) == 3 and \
                not (utils.is_string(args[2]) or args[2] is None):
            args = args[0], args[1], json.dumps(args[2])
        return fun(*args, **kwargs)

    return inner


class Request(object):
    """The Request adapter class"""

    def __init__(self, timeout=None, verify=True, cert=None):
        """
        Create a new request adapter instance.

        :param int timeout: [optional] timeout to use while sending requests
            to consul.
        """
        self.session = requests.Session()
        self.session.verify = verify
        self.session.cert = cert
        self.timeout = timeout

    def delete(self, uri):
        """Perform a HTTP delete

        :param src uri: The URL to send the DELETE to
        :rtype: consulate.api.Response

        """
        LOGGER.debug("DELETE %s", uri)
        return api.Response(self.session.delete(uri, timeout=self.timeout))

    def get(self, uri, timeout=None):
        """Perform a HTTP get

        :param src uri: The URL to send the DELETE to
        :param timeout: How long to wait on the response
        :type timeout: int or float or None
        :rtype: consulate.api.Response

        """
        LOGGER.debug("GET %s", uri)
        try:
            return api.Response(self.session.get(
                uri, timeout=timeout or self.timeout))
        except (requests.exceptions.RequestException,
                OSError, socket.error) as err:
            raise exceptions.RequestError(str(err))

    def get_stream(self, uri):
        """Perform a HTTP get that returns the response as a stream.

        :param src uri: The URL to send the DELETE to
        :rtype: iterator

        """
        LOGGER.debug("GET Stream from %s", uri)
        try:
            response = self.session.get(uri, stream=True)
        except (requests.exceptions.RequestException,
                OSError, socket.error) as err:
            raise exceptions.RequestError(str(err))
        if utils.response_ok(response):
            for line in response.iter_lines():  # pragma: no cover
                yield line.decode('utf-8')

    @prepare_data
    def put(self, uri, data=None, timeout=None):
        """Perform a HTTP put

        :param src uri: The URL to send the DELETE to
        :param str data: The PUT data
        :param timeout: How long to wait on the response
        :type timeout: int or float or None
        :rtype: consulate.api.Response

        """
        LOGGER.debug("PUT %s with %r", uri, data)
        headers = {
            'Content-Type': CONTENT_FORM
            if utils.is_string(data) else CONTENT_JSON
        }
        try:
            return api.Response(
                self.session.put(
                    uri, data=data, headers=headers,
                    timeout=timeout or self.timeout))
        except (requests.exceptions.RequestException,
                OSError, socket.error) as err:
            raise exceptions.RequestError(str(err))


class UnixSocketRequest(Request):  # pragma: no cover
    """Use to communicate with Consul over a Unix socket"""

    def __init__(self, timeout=None):
        super(UnixSocketRequest, self).__init__(timeout)
        self.session = requests_unixsocket.Session()

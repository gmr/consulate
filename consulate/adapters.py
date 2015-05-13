"""
HTTP Client Library Adapters

"""
import json
import logging

import requests
import requests_unixsocket

from consulate import api
from consulate import utils

LOGGER = logging.getLogger(__name__)

CONTENT_FORM = 'application/x-www-form-urlencoded; charset=UTF-8'
CONTENT_JSON = 'application/json; charset=UTF-8'


def prepare_data(fun):
    """Decorator for transforming the data being submitted to Consul

    :param function fun: The decorated function

    """

    def inner(*args, **kwargs):
        """Inner wrapper function for the decorator

        :param list args: positional arguments
        :param dict kwargs: keyword arguments

        """
        if kwargs.get('data') and not utils.is_string(kwargs.get('data')):
            kwargs['data'] = json.dumps(kwargs['data'])
        elif len(args) == 3 and not utils.is_string(args[2]):
            args = args[0], args[1], json.dumps(args[2])
        return fun(*args, **kwargs)

    return inner


class Request(object):
    """The Request adapter class"""

    def __init__(self, timeout=None):
        """
        Create a new request adapter instance.

        :param int timeout: [optional] timeout to use while sending requests
            to consul.
        """
        self.session = requests.Session()
        self.timeout = timeout

    def delete(self, uri):
        """Perform a HTTP delete

        :param src uri: The URL to send the DELETE to
        :rtype: consulate.api.Response

        """
        LOGGER.debug("DELETE %s", uri)
        response = self.session.delete(uri, timeout=self.timeout)
        return api.Response(response.status_code, response.content,
                            response.headers)

    def get(self, uri):
        """Perform a HTTP get

        :param src uri: The URL to send the DELETE to
        :rtype: consulate.api.Response

        """
        LOGGER.debug("GET %s", uri)
        response = self.session.get(uri, timeout=self.timeout)
        return api.Response(response.status_code, response.content,
                            response.headers)

    @prepare_data
    def put(self, uri, data=None):
        """Perform a HTTP put

        :param src uri: The URL to send the DELETE to
        :param str data: The PUT data
        :rtype: consulate.api.Response

        """
        LOGGER.debug("PUT %s with %r", uri, data)
        if utils.is_string(data):
            headers = {'Content-Type': CONTENT_FORM}
        else:
            headers = {'Content-Type': CONTENT_JSON}
        if not utils.PYTHON3 and data:
            data = data.encode('utf-8')
        response = self.session.put(uri,
                                    data=data,
                                    headers=headers,
                                    timeout=self.timeout)
        return api.Response(response.status_code, response.content,
                            response.headers)


class UnixSocketRequest(Request):
    """Use to communicate with Consul over a Unix socket"""

    def __init__(self, timeout=None):
        self.session = requests_unixsocket.Session()
        self.timeout = timeout

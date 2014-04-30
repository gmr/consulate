"""
HTTP Client Library Adapters

"""
import base64
import json
import logging
import requests
try:
    from tornado import gen
    from tornado import httpclient
except ImportError:
    gen, httpclient = None, None


LOGGER = logging.getLogger(__name__)


def prepare_data(fun):
    def inner(*args, **kwargs):
        if kwargs.get('data') and not isinstance(kwargs.get('data'), str):
            kwargs['data'] = json.dumps(kwargs['data'])
        elif len(args) == 3 and not isinstance(args[2], str):
            args = args[0], args[1], json.dumps(args[2])
        return fun(*args, **kwargs)
    return inner


class Request(object):

    HEADERS = {'Content-Type': 'application/json'}

    def __init__(self):
        self.session = requests.Session()

    def delete(self, uri):
        LOGGER.debug("DELETE %s", uri)
        response = self.session.delete(uri)
        return Response(response.status_code,
                        response.content,
                        response.headers)

    def get(self, uri):
        LOGGER.debug("GET %s", uri)
        response = self.session.get(uri)
        return Response(response.status_code,
                        response.content,
                        response.headers)

    @prepare_data
    def put(self, uri, data=None):
        LOGGER.debug("PUT %s with %r", uri, data)
        response = self.session.put(uri, headers=self.HEADERS, data=data)
        return Response(response.status_code,
                        response.content,
                        response.headers)


class TornadoRequest(Request):

    def __init__(self):
        if gen is None or httpclient is None:
            raise ImportError('Could not import the required Tornado modules')
        self.session = httpclient.AsyncHTTPClient()

    @gen.coroutine
    def delete(self, uri):
        response = yield self.session.fetch(uri, method="delete")
        raise gen.Return(Response(response.code,
                                  response.body,
                                  response.headers))

    @gen.coroutine
    def get(self, uri):
        response = yield self.session.fetch(uri)
        raise gen.Return(Response(response.code,
                                  response.body,
                                  response.headers))

    @gen.coroutine
    def put(self, uri, headers=None, data=None):
        response = yield self.session.fetch(uri,
                                            headers=self.HEADERS,
                                            body=json.dumps(data))
        raise gen.Return(Response(response.code,
                                  response.body,
                                  response.headers))


class Response(object):

    status_code = None
    body = None
    headers = None

    def __init__(self, status_code, body, headers):
        self.status_code = status_code
        self.body = self._demarshal(body)
        self.headers = headers

    def _demarshal(self, body):
        """Demarshal the request payload.

        :param str body: The string response body
        :rtype: dict or str

        """
        if self.status_code == 200:
            try:
                value = json.loads(body)
            except (TypeError, ValueError):
                return body
            if isinstance(value, bool):
                return value
            if not 'error' in value:
                for row in value:
                    if 'Value' in row:
                        try:
                            row['Value'] = base64.b64decode(row['Value'])
                        except TypeError:
                            pass
                        try:
                            row['Value'] = json.loads(row['Value'])
                        except (TypeError, ValueError):
                            pass
            if isinstance(value, list) and len(value) == 1:
                return value[0]
            return value
        return body

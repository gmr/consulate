"""
HTTP Client Library Adapters

"""
import base64
import logging
import sys
import requests

try:
    import simplejson as json
except ImportError:
    import json

try:
    from tornado import gen
    from tornado import httpclient
except ImportError:
    httpclient = None

    class Gen:
        def coroutine(self, func):
            pass
    gen = Gen()

LOGGER = logging.getLogger(__name__)

CONTENT_FORM = 'application/x-www-form-urlencoded; charset=UTF-8'
CONTENT_JSON = 'application/json; charset=UTF-8'
PYTHON3 = True if sys.version_info > (3, 0, 0) else False


def is_string(value):
    checks = [isinstance(value, bytes), isinstance(value, str)]
    if not PYTHON3:
        checks.append(isinstance(value, unicode))
    return any(checks)


def prepare_data(fun):
    def inner(*args, **kwargs):
        if kwargs.get('data') and not is_string(kwargs.get('data')):
            kwargs['data'] = json.dumps(kwargs['data'])
        elif len(args) == 3 and not is_string(args[2]):
            args = args[0], args[1], json.dumps(args[2])
        return fun(*args, **kwargs)
    return inner


class Request(object):

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
        if is_string(data):
            headers = {'Content-Type': CONTENT_FORM}
        else:
            headers = {'Content-Type': CONTENT_JSON}
        response = self.session.put(uri, data=data.encode('utf-8'),
                                    headers=headers)
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
        if is_string(data):
            headers = {'Content-Type': CONTENT_FORM}
        else:
            headers = {'Content-Type': CONTENT_JSON}
        response = yield self.session.fetch(uri,
                                            headers=headers,
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
            if 'error' not in value:
                for row in value:
                    if 'Value' in row:
                        try:
                            row['Value'] = base64.b64decode(row['Value'])
                            row['Value'] = row['Value'].decode('utf-8')
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

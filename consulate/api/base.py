"""
Base Endpoint class used by all endpoint classes

"""
import base64
import json
try:
    from urllib.parse import urlencode  # Python 3
except ImportError:  # pragma: no cover
    from urllib import urlencode  # Python 2

from consulate import exceptions
from consulate import utils


class Endpoint(object):
    """Base class for API endpoints"""

    KEYWORD = ''

    def __init__(self, uri, adapter, datacenter=None, token=None):
        """Create a new instance of the Endpoint class

        :param str uri: Base URI
        :param consul.adapters.Request adapter: Request adapter
        :param str datacenter: datacenter
        :param str token: Access Token

        """
        self._adapter = adapter
        self._base_uri = '{0}/{1}'.format(uri, self.__class__.__name__.lower())
        self._dc = datacenter
        self._token = token

    def _build_uri(self, params, query_params=None):
        """Build the request URI

        :param list params: List of path parts
        :param dict query_params: Build query parameters

        """
        if not query_params:
            query_params = dict()
        if self._dc:
            query_params['dc'] = self._dc
        if self._token:
            query_params['token'] = self._token
        path = '/'.join(params)
        if query_params:
            return '{0}/{1}?{2}'.format(self._base_uri, path,
                                        urlencode(query_params))
        return '{0}/{1}'.format(self._base_uri, path)

    def _get(self, params, query_params=None, raise_on_404=False):
        """Perform a GET request

        :param list params: List of path parts
        :param dict query_params: Build query parameters

        """
        response = self._adapter.get(self._build_uri(params, query_params))
        if response.status_code == 200:
            return response.body
        elif response.status_code == 401:
            raise exceptions.ACLDisabled(response.body)
        elif response.status_code == 403:
            raise exceptions.Forbidden(response.body)
        elif response.status_code == 404 and raise_on_404:
            raise exceptions.NotFound(response.body)
        return []

    def _get_list(self, params, query_params=None):
        """Return a list queried from Consul

        :param list params: List of path parts
        :param dict query_params: Build query parameters

        """
        result = self._get(params, query_params)
        if isinstance(result, dict):
            return [result]
        return result

    def _get_no_response_body(self, url_parts, query=None):
        return self._adapter.get(self._build_uri(url_parts,
                                                 query)).status_code == 200

    def _get_response_body(self, url_parts, query=None):
        return self._adapter.get(self._build_uri(url_parts, query)).body

    def _put_no_response_body(self, url_parts, query=None, payload=None):
        return self._adapter.put(self._build_uri(url_parts, query),
                                 payload).status_code == 200

    def _put_response_body(self, url_parts, query=None, payload=None):
        return self._adapter.put(self._build_uri(url_parts, query),
                                 payload).body


class Response(object):
    """Used to process and wrap the responses from Consul.

    :param int status_code: HTTP Status code
    :param str body: The response body
    :param dict headers: Response headers

    """
    status_code = None
    body = None
    headers = None

    def __init__(self, status_code, body, headers):
        """Create a new instance of the Response class.

        :param int status_code: HTTP Status code
        :param str body: The response body
        :param dict headers: Response headers

        """
        self.status_code = status_code
        self.body = self._demarshal(body)
        self.headers = headers

    def _demarshal(self, body):
        """Demarshal the request payload.

        :param str body: The string response body
        :rtype: dict or str

        """
        if body is None:
            return None
        if self.status_code == 200:
            try:
                if utils.PYTHON3 and isinstance(body, bytes):
                    try:
                        body = body.decode('utf-8')
                    except UnicodeDecodeError:
                        pass
                value = json.loads(body, encoding='utf-8')
            except (TypeError, ValueError):
                return body
            if value is None:
                return None
            if isinstance(value, bool):
                return value
            if 'error' not in value:
                for row in value:
                    if 'Value' in row:
                        try:
                            row['Value'] = base64.b64decode(row['Value'])
                            if isinstance(row['Value'], bytes):
                                try:
                                    row['Value'] = row['Value'].decode('utf-8')
                                except UnicodeDecodeError:
                                    pass
                        except TypeError:
                            pass
            if isinstance(value, list) and len(value) == 1:
                return value[0]
            return value
        return body

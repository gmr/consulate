"""
Consulate: A client library for Consul

"""
__version__ = '0.4.0'


import logging
try:
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        """Python 2.6 does not have a NullHandler"""
        def emit(self, record):
            """Emit a record
            :param record record: The record to emit
            """
            pass

logging.getLogger('consulate').addHandler(NullHandler())

from consulate import adapters
from consulate import api

DEFAULT_HOST = 'localhost'
DEFAULT_PORT = 8500
SCHEME = 'http'
VERSION = 'v1'


class Consul(object):
    """Access the Consul HTTP API via Python

    :param str host: The host name to connect to (Default: localhost)
    :param int port: The port to connect on (Default: 8500)
    :param str datacenter: Specify a specific data center
    :param str token: Specify a ACL token to use

    """
    def __init__(self, host=DEFAULT_HOST, port=DEFAULT_PORT,
                 datacenter=None, token=None):
        """Create a new instance of the Consul class"""
        base_uri = self._base_uri(host, port)
        self._adapter = adapters.Request()
        self._acl = api.ACL(base_uri, self._adapter, datacenter, token)
        self._agent = api.Agent(base_uri, self._adapter, datacenter, token)
        self._catalog = api.Catalog(base_uri, self._adapter, datacenter, token)
        self._event = api.Event(base_uri, self._adapter, datacenter, token)
        self._health = api.Health(base_uri, self._adapter, datacenter, token)
        self._kv = api.KV(base_uri, self._adapter, datacenter, token)
        self._session = api.Session(base_uri, self._adapter, datacenter, token)
        self._status = api.Status(base_uri, self._adapter, datacenter, token)

    @property
    def acl(self):
        """Access the Consul
        `ACL <https://www.consul.io/docs/agent/http.html#acl>`_ API

        :rtype: :py:class:`consulate.api_old.ACL`

        """
        return self._acl

    @property
    def agent(self):
        """Access the Consul
        `Agent <https://www.consul.io/docs/agent/http.html#agent>`_ API

        :rtype: :py:class:`consulate.api.Agent`

        """
        return self._agent

    @property
    def catalog(self):
        """Access the Consul
        `Catalog <https://www.consul.io/docs/agent/http.html#catalog>`_ API

        :rtype: :py:class:`consulate.api.Catalog`

        """
        return self._catalog

    @property
    def event(self):
        """Access the Consul
        `Events <https://www.consul.io/docs/agent/http.html#events>`_ API

        :rtype: :py:class:`consulate.api_old.Event`

        """
        return self._event

    @property
    def health(self):
        """Access the Consul
        `Health <https://www.consul.io/docs/agent/http.html#health>`_ API

        :rtype: :py:class:`consulate.api.Health`

        """
        return self._health

    @property
    def kv(self):
        """Access the Consul
        `KV <https://www.consul.io/docs/agent/http.html#kv>`_ API

        :rtype: :py:class:`consulate.api.KV`

        """
        return self._kv

    @property
    def session(self):
        """Access the Consul
        `Session <https://www.consul.io/docs/agent/http.html#session>`_ API

        :rtype: :py:class:`consulate.api_old.Session`

        """
        return self._session

    @property
    def status(self):
        """Access the Consul
        `Status <https://www.consul.io/docs/agent/http.html#status>`_ API

        :rtype: :py:class:`consulate.api_old.Status`

        """
        return self._status

    @staticmethod
    def _base_uri(host, port):
        """Return the base URI to use for API requests

        :param str host: The host name to connect to (Default: localhost)
        :param int port: The port to connect on (Default: 8500)
        :rtype: str

        """
        return '{0}://{1}:{2}/{3}'.format(SCHEME, host, port, VERSION)


# Backwards compatibility with 0.3.0
Session = Consul

"""
Consulate: A client library for Consul

"""
__version__ = '0.6.0'

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
from consulate import utils

from consulate.exceptions import *

DEFAULT_HOST = 'localhost'
DEFAULT_PORT = 8500
DEFAULT_SCHEME = 'http'
VERSION = 'v1'


class Consul(object):
    """Access the Consul HTTP API via Python.

    The default values connect to Consul via ``localhost:8500`` via http. If
    you want to connect to Consul via a local UNIX socket, you'll need to
    override both the ``scheme``, ``port`` and the ``adapter`` like so:

    .. code:: python

        consul = consulate.Consul('/path/to/socket', None, scheme='http+unix',
                                  adapter=consulate.adapters.UnixSocketRequest)
        services = consul.agent.services()

    :param str host: The host name to connect to (Default: localhost)
    :param int port: The port to connect on (Default: 8500)
    :param str datacenter: Specify a specific data center
    :param str token: Specify a ACL token to use
    :param str scheme: Specify the scheme (Default: http)
    :param class adapter: Specify to override the request adapter
        (Default: :py:class:`consulate.adapters.Request`)

    """

    def __init__(self,
                 host=DEFAULT_HOST,
                 port=DEFAULT_PORT,
                 datacenter=None,
                 token=None,
                 scheme=DEFAULT_SCHEME,
                 adapter=None):
        """Create a new instance of the Consul class"""
        base_uri = self._base_uri(scheme, host, port)
        self._adapter = adapter() if adapter else adapters.Request()
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

        :rtype: :py:class:`consulate.api.acl.ACL`

        """
        return self._acl

    @property
    def agent(self):
        """Access the Consul
        `Agent <https://www.consul.io/docs/agent/http.html#agent>`_ API

        :rtype: :py:class:`consulate.api.agent.Agent`

        """
        return self._agent

    @property
    def catalog(self):
        """Access the Consul
        `Catalog <https://www.consul.io/docs/agent/http.html#catalog>`_ API

        :rtype: :py:class:`consulate.api.catalog.Catalog`

        """
        return self._catalog

    @property
    def event(self):
        """Access the Consul
        `Events <https://www.consul.io/docs/agent/http.html#events>`_ API

        :rtype: :py:class:`consulate.api.event.Event`

        """
        return self._event

    @property
    def health(self):
        """Access the Consul
        `Health <https://www.consul.io/docs/agent/http.html#health>`_ API

        :rtype: :py:class:`consulate.api.health.Health`

        """
        return self._health

    @property
    def kv(self):
        """Access the Consul
        `KV <https://www.consul.io/docs/agent/http.html#kv>`_ API

        :rtype: :py:class:`consulate.api.kv.KV`

        """
        return self._kv

    @property
    def session(self):
        """Access the Consul
        `Session <https://www.consul.io/docs/agent/http.html#session>`_ API

        :rtype: :py:class:`consulate.api.session.Session`

        """
        return self._session

    @property
    def status(self):
        """Access the Consul
        `Status <https://www.consul.io/docs/agent/http.html#status>`_ API

        :rtype: :py:class:`consulate.api.status.Status`

        """
        return self._status

    @staticmethod
    def _base_uri(scheme, host, port):
        """Return the base URI to use for API requests. Set ``port`` to None
        when creating a UNIX Socket URL.

        :param str scheme: The scheme to use (Default: http)
        :param str host: The host name to connect to (Default: localhost)
        :param int|None port: The port to connect on (Default: 8500)
        :rtype: str

        """
        if port:
            return '{0}://{1}:{2}/{3}'.format(scheme, host, port, VERSION)
        return '{0}://{1}/{2}'.format(scheme, utils.quote(host, ''), VERSION)

# Backwards compatibility with 0.3.0
Session = Consul

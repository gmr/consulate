"""
Consul client object

"""
import os
from consulate import adapters, api, utils

DEFAULT_HOST = os.environ.get('CONSUL_HOST') or 'localhost'
DEFAULT_PORT = os.environ.get('CONSUL_PORT') or 8500
DEFAULT_ADDR = os.environ.get('CONSUL_HTTP_ADDR')
DEFAULT_SCHEME = 'http'
DEFAULT_TOKEN = os.environ.get('CONSUL_HTTP_TOKEN')
API_VERSION = 'v1'


class Consul(object):
    """Access the Consul HTTP API via Python.

    The default values connect to Consul via ``localhost:8500`` via http. If
    you want to connect to Consul via a local UNIX socket, you'll need to
    override both the ``scheme``, ``port`` and the ``adapter`` like so:

    .. code:: python

        consul = consulate.Consul('/path/to/socket', None, scheme='http+unix',
                                  adapter=consulate.adapters.UnixSocketRequest)
        services = consul.agent.services()

    :param str addr: The CONSUL_HTTP_ADDR if available (Default: None)
    :param str host: The host name to connect to (Default: localhost)
    :param int port: The port to connect on (Default: 8500)
    :param str datacenter: Specify a specific data center
    :param str token: Specify a ACL token to use
    :param str scheme: Specify the scheme (Default: http)
    :param class adapter: Specify to override the request adapter
        (Default: :py:class:`consulate.adapters.Request`)
    :param bool/str verify: Specify how to verify TLS certificates
    :param tuple cert: Specify client TLS certificate and key files
    :param float timeout: Timeout in seconds for API requests (Default: None)

    """
    def __init__(self,
                 addr=DEFAULT_ADDR,
                 host=DEFAULT_HOST,
                 port=DEFAULT_PORT,
                 datacenter=None,
                 token=DEFAULT_TOKEN,
                 scheme=DEFAULT_SCHEME,
                 adapter=None,
                 verify=True,
                 cert=None,
                 timeout=None):
        """Create a new instance of the Consul class"""
        base_uri = self._base_uri(addr=addr,
                                  scheme=scheme,
                                  host=host,
                                  port=port)
        self._adapter = adapter() if adapter else adapters.Request(
            timeout=timeout, verify=verify, cert=cert)
        self._acl = api.ACL(base_uri, self._adapter, datacenter, token)
        self._agent = api.Agent(base_uri, self._adapter, datacenter, token)
        self._catalog = api.Catalog(base_uri, self._adapter, datacenter, token)
        self._event = api.Event(base_uri, self._adapter, datacenter, token)
        self._health = api.Health(base_uri, self._adapter, datacenter, token)
        self._coordinate = api.Coordinate(base_uri, self._adapter, datacenter,
                                          token)
        self._kv = api.KV(base_uri, self._adapter, datacenter, token)
        self._session = api.Session(base_uri, self._adapter, datacenter, token)
        self._status = api.Status(base_uri, self._adapter, datacenter, token)
        self._lock = api.Lock(base_uri, self._adapter, self._session,
                              datacenter, token)

    @property
    def acl(self):
        """Access the Consul
        `ACL <https://www.consul.io/docs/agent/http/acl.html>`_ API

        :rtype: :py:class:`consulate.api.acl.ACL`

        """
        return self._acl

    @property
    def agent(self):
        """Access the Consul
        `Agent <https://www.consul.io/docs/agent/http/agent.html>`_ API

        :rtype: :py:class:`consulate.api.agent.Agent`

        """
        return self._agent

    @property
    def catalog(self):
        """Access the Consul
        `Catalog <https://www.consul.io/docs/agent/http/catalog.html>`_ API

        :rtype: :py:class:`consulate.api.catalog.Catalog`

        """
        return self._catalog

    @property
    def event(self):
        """Access the Consul
        `Events <https://www.consul.io/docs/agent/http/event.html>`_ API

        :rtype: :py:class:`consulate.api.event.Event`

        """
        return self._event

    @property
    def health(self):
        """Access the Consul
        `Health <https://www.consul.io/docs/agent/http/health.html>`_ API

        :rtype: :py:class:`consulate.api.health.Health`

        """
        return self._health

    @property
    def coordinate(self):
        """Access the Consul
        `Coordinate <https://www.consul.io/api/coordinate.html#read-lan-coordinates-for-a-node>`_ API

        :rtype: :py:class:`consulate.api.coordinate.Coordinate`

        """
        return self._coordinate

    @property
    def kv(self):
        """Access the Consul
        `KV <https://www.consul.io/docs/agent/http/kv.html>`_ API

        :rtype: :py:class:`consulate.api.kv.KV`

        """
        return self._kv

    @property
    def lock(self):
        """Wrapper for easy :class:`~consulate.api.kv.KV` locks.
        `Semaphore <https://www.consul.io/docs/guides/semaphore.html>` _Guide
        Example:

        .. code:: python

            import consulate

            consul = consulate.Consul()
            with consul.lock.acquire('my-key'):
                print('Locked: {}'.format(consul.lock.key))
                # Do stuff

        :rtype: :class:`~consulate.api.lock.Lock`

        """
        return self._lock

    @property
    def session(self):
        """Access the Consul
        `Session <https://www.consul.io/docs/agent/http/session.html>`_ API

        :rtype: :py:class:`consulate.api.session.Session`

        """
        return self._session

    @property
    def status(self):
        """Access the Consul
        `Status <https://www.consul.io/docs/agent/http/status.html>`_ API

        :rtype: :py:class:`consulate.api.status.Status`

        """
        return self._status

    @staticmethod
    def _base_uri(scheme, host, port, addr=None):
        """Return the base URI to use for API requests. Set ``port`` to None
        when creating a UNIX Socket URL.

        :param str scheme: The scheme to use (Default: http)
        :param str host: The host name to connect to (Default: localhost)
        :param int|None port: The port to connect on (Default: 8500)
        :rtype: str

        """
        if addr is None:
            if port:
                return '{0}://{1}:{2}/{3}'.format(scheme, host, port,
                                                  API_VERSION)
            return '{0}://{1}/{2}'.format(scheme, utils.quote(host, ''),
                                          API_VERSION)
        return '{0}/{1}'.format(addr, API_VERSION)

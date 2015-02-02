"""
consulate.api
=============
The :py:mod:`consulate.api` module exposes the main classes in consulate for
end-user use.

Primary use is focused on the :py:class:`Session <consulate.api.Session>` or the
:py:class:`TornadoSession <consulate.api.TornadoSession>` classes which then
wrap access to consul's HTTP API via the :py:class:`ACL <consulate.api.ACL>`,
:py:class:`Agent <consulate.api.Agent>`,
:py:class:`Catalog <consulate.api.Catalog>`,
:py:class:`Events <consulate.api.Events>`,
:py:class:`Health <consulate.api.Health>`, :py:class:`KV <consulate.api.KV>`,
and :py:class:`Status <consulate.api.Status>` classes.

Example use:

.. code:: python

    session = consulate.Session('127.0.0.1', 8500, 'dc1', 'acl-token-value)
    session.agent.checks()

"""
import logging
try:
    from urllib.parse import urlencode  # Python 3
except ImportError:  # pragma: no cover
    from urllib import urlencode        # Python 2

from consulate import adapters

LOGGER = logging.getLogger(__name__)

DEFAULT_HOST = 'localhost'
DEFAULT_PORT = 8500


class Session(object):
    """Access the Consul HTTP API via Python

    :param str host: The host name to connect to (Default: localhost)
    :param int port: The port to connect on (Default: 8500)
    :param str dc: Specify a specific data center
    :param str token: Specify a ACL token to use

    """
    SCHEME = 'http'
    VERSION = 'v1'

    def __init__(self, host=DEFAULT_HOST, port=DEFAULT_PORT, dc=None,
                 token=None):
        base_uri = self._base_uri(host, port)
        self._adapter = adapters.Request()
        self._acl = None
        self._agent = Agent(base_uri, self._adapter, dc, token)
        self._catalog = Catalog(base_uri, self._adapter, dc, token)
        self._events = None
        self._health = Health(base_uri, self._adapter, dc, token)
        self._kv = KV(base_uri, self._adapter, dc, token)
        self._status = Status(base_uri, self._adapter, dc, token)

    @property
    def acl(self):
        """Access the Consul
        `ACL <https://www.consul.io/docs/agent/http.html#acl>`_ API

        :rtype: :py:class:`consulate.api.ACL`

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
    def events(self):
        """Access the Consul
        `Events <https://www.consul.io/docs/agent/http.html#events>`_ API

        :rtype: :py:class:`consulate.api.Events`

        """
        return self._events

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
    def status(self):
        """Access the Consul
        `Status <https://www.consul.io/docs/agent/http.html#status>`_ API

        :rtype: :py:class:`consulate.api.Status`

        """
        return self._status

    def _base_uri(self, host, port):
        """Return the base URI to use for API requests

        :param str host: The host name to connect to (Default: localhost)
        :param int port: The port to connect on (Default: 8500)
        :rtype: str

        """
        return '{0}://{1}:{2}/{3}'.format(self.SCHEME, host, port, self.VERSION)


class TornadoSession(Session):
    pass


class _Endpoint(object):
    """Base class for API endpoints"""

    KEYWORD = ''

    def __init__(self, uri, adapter, dc=None, token=None):
        self._adapter = adapter
        self._base_uri = '{0}/{1}'.format(uri, self.__class__.__name__.lower())
        self._dc = dc
        self._token = token

    def _build_uri(self, params, query_params=None):
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

    def _get(self, params, query_params=None):
        response = self._adapter.get(self._build_uri(params, query_params))
        if response.status_code == 200:
            return response.body
        return []

    def _get_list(self, params, query_params=None):
        result = self._get(params, query_params)
        if isinstance(result, dict):
            return [result]
        return result


class KV(_Endpoint):
    """The :py:class:`consul.api.KV` class implements a :py:class:`dict` like
    interface for working with the Key/Value service. Simply use items on the
    :py:class:`consulate.Session` like you would with a :py:class:`dict` to
    :py:meth:`get <consulate.api.KV.get>`,
    :py:meth:`set <consulate.api.KV.set>`, or
    :py:meth:`delete <consulate.api.KV.delete>` values in the key/value store.

    Additionally, :py:class:`KV <consulate.api.KV>` acts as an
    :py:meth:`iterator <consulate.api.KV.__iter__>`, providing methods to
    iterate over :py:meth:`keys <consulate.api.KV.keys>`,
    :py:meth:`values <consulate.api.KV.values>`,
    :py:meth:`keys and values <consulate.api.KV.iteritems>`, etc.

    Should you need access to get or set the flag value, the
    :py:meth:`get_record <consulate.api.KV.get_record>`,
    :py:meth:`set_record <consulate.api.KV.set_record>`,
    and :py:meth:`records <consulate.api.KV.records>` provide a way to access
    the additional fields exposed by the KV service.

    """
    def __contains__(self, item):
        """Return True if there is a value set in the Key/Value service for the
        given key.

        :param str item: The key to check for
        :rtype: bool

        """
        item = item.lstrip('/')
        response = self._adapter.get(self._build_uri([item]))
        return response.status_code == 200

    def __delitem__(self, item):
        """Delete an item from the Key/Value service

        :param str item: The key name
        :raises: KeyError

        """
        item = item.lstrip('/')
        response = self._adapter.delete(self._build_uri([item]))
        if response.status_code != 200:
            raise KeyError(
                'Error removing "{0}" ({1})'.format(item, response.status_code))

    def __getitem__(self, item):
        """Get a value from the Key/Value service, returning it fully
        demarshaled if possible.

        :param str item: The item name
        :rtype: mixed
        :raises: KeyError

        """
        value = self._get_item(item)
        try:
            return value.get('Value', value)
        except AttributeError:
            return value

    def __iter__(self):
        """Iterate over all the keys in the Key/Value service

        :rtype: iterator

        """
        for key in self.keys():
            yield key

    def __len__(self):
        """Return the number if items in the Key/Value service

        :return: int

        """
        return len(self._get_all_items())

    def __setitem__(self, item, value):
        """Set a value in the Key/Value service, using the CAS mechanism
        to ensure that the set is atomic. If the value passed in is not a
        string, an attempt will be made to JSON encode the value prior to
        setting it.

        :param str item: The key to set
        :param mixed value: The value to set
        :raises: KeyError

        """
        self._set_item(item, value)

    def delete(self, item):
        """Delete an item from the Key/Value service

        :param str item: The item key
        :raises: KeyError

        """
        return self.__delitem__(item)

    def get(self, item, default=None):
        """Get a value from the Key/Value service, returning it fully
        demarshaled if possible.

        :param str item: The item key
        :rtype: mixed
        :raises: KeyError

        """
        try:
            return self.__getitem__(item)
        except KeyError:
            return default

    def get_record(self, item, default=None):
        """Get the full record from the Key/Value service, returning
        all fields including the flag.

        :param str item: The item key
        :rtype: dict
        :raises: KeyError

        """
        try:
            return self._get_item(item)
        except KeyError:
            return default

    def find(self, prefix, separator=None):
        """Find all keys with the specified prefix, returning a dict of
        matches.

        *Example:*

        .. code:: python

            >>> session.kv.find('b')
            {'baz': 'qux', 'bar': 'baz'}

        :param str prefix: The prefix to search with
        :rtype: dict

        """
        query_params = {'recurse': None}
        if separator:
            query_params['keys'] = prefix
            query_params['separator'] = separator
        response = self._get_list([prefix.lstrip('/')], query_params)
        if separator:
            results = response
        else:
            results = {}
            for row in response:
                results[row['Key']] = row['Value']
        return results

    def items(self):
        """Return a dict of all of the key/value pairs in the Key/Value service

        *Example:*

        .. code:: python

            >>> session.kv.items()
            {'foo': 'bar', 'bar': 'baz', 'quz': True, 'corgie': 'dog'}

       :rtype: dict

        """
        return [{item['Key']: item['Value']} for item in self._get_all_items()]

    def iteritems(self):
        """Iterate over the dict of key/value pairs in the Key/Value service

        *Example:*

        .. code:: python

            >>> for key, value in session.kv.iteritems():
            ...     print(key, value)
            ...
            (u'bar', 'baz')
            (u'foo', 'bar')
            (u'quz', True)

       :rtype: iterator

        """
        for item in self._get_all_items():
            yield item['Key'], item['Value']

    def keys(self):
        """Return a list of all of the keys in the Key/Value service

        *Example:*

        .. code:: python

            >>> session.kv.keys()
            [u'bar', u'foo', u'quz']

        :rtype: list

        """
        return sorted([row['Key'] for row in self._get_all_items()])

    def records(self):
        """Return a list of tuples for all of the records in the Key/Value
        service

        *Example:*

        .. code:: python

            >>> session.kv.records()
            [(u'bar', 0, 'baz'),
             (u'corgie', 128, 'dog'),
             (u'foo', 0, 'bar'),
             (u'quz', 0, True)]

        :rtype: list of (Key, Flags, Value)

        """
        return [(item['Key'], item['Flags'], item['Value'])
                for item in self._get_all_items()]

    def set(self, item, value):
        """Set a value in the Key/Value service, using the CAS mechanism
        to ensure that the set is atomic. If the value passed in is not a
        string, an attempt will be made to JSON encode the value prior to
        setting it.

        :param str item: The key to set
        :param mixed value: The value to set
        :raises: KeyError

        """
        return self.__setitem__(item, value)

    def set_record(self, item, flags=0, value=None):
        """Set a full record, including the item flag

        :param str item: The key to set
        :param mixed value: The value to set

        """
        self._set_item(item, value, flags)

    def values(self):
        """Return a list of all of the values in the Key/Value service

        *Example:*

        .. code:: python

            >>> session.kv.values()
            [True, 'bar', 'baz']

        :rtype: list

        """
        return [row['Value'] for row in self._get_all_items()]

    def _get_all_items(self):
        """Internal method to return a list of all items in the Key/Value
        service

        :rtype: list

        """
        return self._get_list([''], {'recurse': None})

    def _get_item(self, item):
        """Internal method to get the full item record from the Key/Value
        service

        :param str item: The item to get
        :rtype: dict
        :raises: KeyError

        """
        item = item.lstrip('/')
        response = self._adapter.get(self._build_uri([item]))
        if response.status_code == 200:
            return response.body
        elif response.status_code == 404:
            raise KeyError('Key not found ({0})'.format(item))
        else:
            raise KeyError(
                'Unknown response ({0})'.format(response.status_code))

    def _set_item(self, item, value, flags=None):
        """Internal method for setting a key/value pair with flags in the
        Key/Value service

        :param str item: The key to set
        :param mixed value: The value to set
        :param int flags: User defined flags to set
        :raises: KeyError

        """
        item = item.lstrip('/')
        response = self._adapter.get(self._build_uri([item]))
        index = 0

        try:
            if isinstance(value, (str, unicode)):
                value = value.encode('utf-8')
        except NameError:  #in Python3 str is unicode by default
            if isinstance(value, str):
                value = value.encode('utf-8')

        if response.status_code == 200:
            index = response.body.get('ModifyIndex')
            if response.body.get('Value') == value:
                return True
        query_params = {'index': index}
        if flags is not None:
            query_params['flags'] = flags
        response = self._adapter.put(self._build_uri([item], query_params),
                                     value)
        if not response.status_code == 200 or not response.body:
            raise KeyError(
                'Error setting "{0}" ({1})'.format(item, response.status_code))


class Agent(_Endpoint):
    """The Consul agent is the core process of Consul. The agent maintains
    membership information, registers services, runs checks, responds to
    queries and more. The agent must run on every node that is part of a
    Consul cluster.

    """
    def __init__(self, uri, adapter, dc=None, token=None):
        super(Agent, self).__init__(uri, adapter, dc, token)
        self.check = Agent.Check(self._base_uri, adapter, dc, token)
        self.service = Agent.Service(self._base_uri, adapter, dc, token)

    class Check(_Endpoint):
        """One of the primary roles of the agent is the management of system
        and application level health checks. A health check is considered to be
        application level if it associated with a service. A check is defined
        in a configuration file, or added at runtime over the HTTP interface.

        There are two different kinds of checks:

            - Script + Interval: These checks depend on invoking an external
                                 application which does the health check and
                                 exits with an appropriate exit code,
                                 potentially generating some output. A script
                                 is paired with an invocation interval
                                 (e.g. every 30 seconds). This is similar to
                                 the Nagios plugin system.

            - TTL: These checks retain their last known state for a given TTL.
                   The state of the check must be updated periodically
                   over the HTTP interface. If an external system fails to
                   update the status within a given TTL, the check is set to
                   the failed state. This mechanism is used to allow an
                   application to directly report it's health. For example,
                   a web app can periodically curl the endpoint, and if the
                   app fails, then the TTL will expire and the health check
                   enters a critical state. This is conceptually similar to a
                   dead man's switch.

        """
        def register(self, name, script, check_id=None, interval=None,
                     ttl=None, notes=None):
            """Add a new check to the local agent. Checks are either a script
            or TTL type. The agent is responsible for managing the status of
            the check and keeping the Catalog in sync.

            The ``name`` field is mandatory, as is either ``script`` and
            ``interval`` or ``ttl``. Only one of ``script`` and ``interval``
            or ``ttl`` should be provided.  If an ``check_id`` is not
            provided, it is set to ``name``. You cannot have  duplicate
            ``check_id`` entries per agent, so it may be necessary to provide
            a ``check_id``. The ``notes`` field is not used by Consul, and is
            meant to be  human readable.

            If a ``script`` is provided, the check type is a script, and Consul
            will evaluate the script every ``interval`` to update the status.
            If a ``ttl`` type is used, then the ``ttl`` update APIs must be
            used to periodically update the state of the check.

            :param str name: The check name
            :param str script: The path to the script to run
            :param str check_id: The optional check id
            :param int interval: The interval to run the check
            :param int ttl: The ttl to specify for the check
            :rtype: bool
            :raises: ValueError

            """
            # Validate the parameters
            if script and not interval:
                raise ValueError('Must specify interval when using script')
            elif script and ttl:
                raise ValueError('Can not specify script and ttl together')

            # Register the check
            response = self._adapter.put(self._build_uri(['register']),
                                         {'ID': check_id,
                                          'Name': name,
                                          'Notes': notes,
                                          'Script': script,
                                          'Interval': interval,
                                          'TTL': ttl})
            return response.status_code == 200

        def deregister(self, check_id):
            """Remove a check from the local agent. The agent will take care
            of deregistering the check with the Catalog.

            :param str check_id: The check id

            """
            response = self._adapter.get(self._build_uri(['deregister',
                                                          check_id]))
            return response.status_code == 200

        def ttl_pass(self, check_id):
            """This endpoint is used with a check that is of the TTL type.
            When this endpoint is accessed, the status of the check is set to
            "passing", and the TTL clock is reset.

            :param str check_id: The check id

            """
            response = self._adapter.get(self._build_uri(['pass', check_id]))
            return response.status_code == 200

        def ttl_warn(self, check_id):
            """This endpoint is used with a check that is of the TTL type.
            When this endpoint is accessed, the status of the check is set
            to "warning", and the TTL clock is reset.

            :param str check_id: The check id

            """
            response = self._adapter.get(self._build_uri(['warn', check_id]))
            return response.status_code == 200

        def ttl_fail(self, check_id):
            """This endpoint is used with a check that is of the TTL type.
            When this endpoint is accessed, the status of the check is set
            to "critical", and the TTL clock is reset.

            :param str check_id: The check id

            """
            response = self._adapter.get(self._build_uri(['fail', check_id]))
            return response.status_code == 200

    class Service(_Endpoint):
        """One of the main goals of service discovery is to provide a catalog
        of available services. To that end, the agent provides a simple
        service definition format to declare the availability of a service, a
        nd to potentially associate it with a health check. A health check is
        considered to be application level if it associated with a service. A
        service is defined in a configuration file, or added at runtime over
        the HTTP interface.

        """
        CHECK_EXCEPTION = 'check must be a tuple of script, interval, and ttl'

        def register(self, name, service_id=None, port=None,
                     tags=None, check=None, interval=None, ttl=None):
            """Add a new service to the local agent.

            :param str name: The name of the service
            :param str service_id: The id for the service (optional)
            :param int port: The service port
            :param list tags: A list of tags for the service
            :param str check: The path to the check to run
            :param str interval: The script execution interval
            :param str ttl: The TTL for external script check pings
            :rtype: bool
            :raises: ValueError

            """
            # Validate the parameters
            if port and not isinstance(port, int):
                raise ValueError('port must be an integer')
            elif tags and not isinstance(tags, list):
                raise ValueError('tags must be a list of strings')
            elif check and ttl:
                raise ValueError('Can not specify both a check and ttl')

            # Build the payload to send to consul
            payload = {'id': service_id,
                       'name': name,
                       'port': port,
                       'tags': tags,
                       'check': {'script': check,
                                 'interval': interval,
                                 'ttl': ttl}}

            for key in list(payload.keys()):
                if payload[key] is None:
                    del payload[key]

            # Register the service
            result = self._adapter.put(self._build_uri(['register']), payload)
            return result.status_code == 200

        def deregister(self, service_id):
            """Deregister the service from the local agent. The agent will
            take care of deregistering the service with the Catalog. If there
            is an associated check, that is also deregistered.

            :param str service_id: The service id to deregister
            :rtype: bool

            """
            result = self._adapter.get(self._build_uri(['deregister',
                                                        service_id]))
            return result.status_code == 200

    def checks(self):
        """return the all the checks that are registered with the local agent.
        These checks were either provided through configuration files, or
        added dynamically using the HTTP API. It is important to note that
        the checks known by the agent may be different than those reported
        by the Catalog. This is usually due to changes being made while there
        is no leader elected. The agent performs active anti-entropy, so in
        most situations everything will be in sync within a few seconds.

        :rtype: list

        """
        return self._get_list(['checks'])

    def force_leave(self, node):
        """Instructs the agent to force a node into the left state. If a node
        fails unexpectedly, then it will be in a "failed" state. Once in this
        state, Consul will attempt to reconnect, and additionally the services
        and checks belonging to that node will not be cleaned up. Forcing a
        node into the left state allows its old entries to be removed.

        """
        result = self._adapter.get(self._build_uri(['force-leave', node]))
        return result.status_code == 200

    def join(self, address, wan=False):
        """This endpoint is hit with a GET and is used to instruct the agent
        to attempt to connect to a given address. For agents running in
        server mode, setting wan=True causes the agent to attempt to join
        using the WAN pool.

        :param str address: The address to join
        :param bool wan: Join a WAN pool as a server
        :rtype: bool

        """
        query_params = {'wan': 1} if wan else None
        result = self._adapter.get(self._build_uri(['join', address],
                                                   query_params))
        return result.status_code == 200

    def members(self):
        """Returns the members the agent sees in the cluster gossip pool.
        Due to the nature of gossip, this is eventually consistent and the
        results may differ by agent. The strongly consistent view of nodes
        is instead provided by ``Consulate.catalog.nodes``.

        :rtype: list

        """
        return self._get_list(['members'])

    def services(self):
        """return the all the services that are registered with the local
        agent. These services were either provided through configuration
        files, or added dynamically using the HTTP API. It is important to
        note that the services known by the agent may be different than those
        ]reported by the Catalog. This is usually due to changes being made
        while there is no leader elected. The agent performs active
        anti-entropy, so in most situations everything will be in sync
        within a few seconds.

        :rtype: list

        """
        return self._get_list(['services'])


class Catalog(_Endpoint):
    """The Consul agent is the core process of Consul. The agent maintains
    membership information, registers services, runs checks, responds to
    queries and more. The agent must run on every node that is part of a
    Consul cluster.

    """
    def __init__(self, uri, adapter, dc=None, token=None):
        super(Catalog, self).__init__(uri, adapter, dc, token)

    def register(self,  node, address, datacenter=None,
                 service=None, check=None):
        """A a low level mechanism for directly registering or updating
        entries in the catalog. It is usually recommended to use the agent
        local endpoints, as they are simpler and perform anti-entropy.

        The behavior of the endpoint depends on what keys are provided. The
        endpoint requires Node and Address to be provided, while Datacenter
        will be defaulted to match that of the agent. If only those are
        provided, the endpoint will register the node with the catalog.

        If the Service key is provided, then the service will also be
        registered. If ID is not provided, it will be defaulted to Service.
        It is mandated that the ID be node-unique. Both Tags and Port can
        be omitted.

        If the Check key is provided, then a health check will also be
        registered. It is important to remember that this register API is
        very low level. This manipulates the health check entry, but does
        not setup a script or TTL to actually update the status. For that
        behavior, an agent local check should be setup.

        The CheckID can be omitted, and will default to the Name. Like
        before, the CheckID must be node-unique. The Notes is an opaque
        field that is meant to hold human readable text. If a ServiceID is
        provided that matches the ID of a service on that node, then the
        check is treated as a service level health check, instead of a node
        level health check. Lastly, the status must be one of "unknown",
        "passing", "warning", or "critical". The "unknown" status is used to
        indicate that the initial check has not been performed yet.

        It is important to note that Check does not have to be provided
        with Service and visa-versa. They can be provided or omitted at will.
        
        Example service dict:
        
        .. code:: python

            'Service': {
                'ID': 'redis1',
                'Service': 'redis',
                'Tags': ['master', 'v1'],
                'Port': 8000,
            }
            
        Example check dict:
            
        .. code:: python

            'Check': {
                'Node': 'foobar',
                'CheckID': 'service:redis1',
                'Name': 'Redis health check',
                'Notes': 'Script based health check',
                'Status': 'passing',
                'ServiceID': 'redis1'
            }


        :param str node: The node name
        :param str address: The node address
        :param str datacenter: The optional node datacenter
        :param dict service: An optional node service
        :param dict check: An optional node check

        :rtype: bool
        
        """
        payload = {'Node': node, 'Address': address}
        if datacenter:
            payload['Datacenter'] = datacenter
        if service:
            payload['Service'] = service
        if check:
            payload['Check'] = check
        response = self._adapter.put(self._build_uri(['register']), payload)
        return response.status_code == 200

    def deregister(self, node, datacenter=None,
                   check_id=None, service_id=None):
        """Directly remove entries in the catalog. It is usually recommended
        to use the agent local endpoints, as they are simpler and perform
        anti-entropy.

        The behavior of the endpoint depends on what keys are provided. The
        endpoint requires ``node`` to be provided, while ``datacenter`` will
        be defaulted to match that of the agent. If only ``node`` is provided,
        then the node, and all associated services and checks are deleted. If
        ``check_id`` is provided, only that check belonging to the node is
        removed. If ``service_id`` is provided, then the service along with
        it's associated health check (if any) is removed.

        :param str node: The node for the action
        :param str datacenter: The optional datacenter for the node
        :param str check_id: The optional check_id to remove
        :param str service_id: The optional service_id to remove
        :rtype: bool
        
        """
        payload = {'Node': node}
        if datacenter:
            payload['Datacenter'] = datacenter
        if check_id:
            payload['CheckID'] = check_id
        if service_id:
            payload['ServiceID'] = service_id
        response = self._adapter.put(self._build_uri(['deregister']), payload)
        return response.status_code == 200

    def datacenters(self):
        """Return all the datacenters that are known by the Consul server.

        :rtype: list

        """
        return self._get_list(['datacenters'])

    def node(self, node_id):
        """Return the node data for the specified node

        :param str node_id: The node ID
        :rtype: dict

        """
        return self._get(['node', node_id])

    def nodes(self):
        """Return all of the nodes for the current datacenter.

        :rtype: list

        """
        return self._get_list(['nodes'])

    def service(self, service_id):
        """Return the service details for the given service

        :param str service_id: The service id
        :rtype: list

        """
        return self._get_list(['service', service_id])

    def services(self):
        """Return a list of all of the services for the current datacenter.

        :rtype: list

        """
        return self._get_list(['services'])


class Health(_Endpoint):
    """Used to query health related information. It is provided separately
    from the Catalog, since users may prefer to not use the health checking
    mechanisms as they are totally optional. Additionally, some of the query
    results from the Health system are filtered, while the Catalog endpoints
    provide the raw entries.

    """
    def checks(self, service_id):
        """Return checks for the given service.

        :param str service_id: The service ID
        :rtype: list

        """
        return self._get_list(['checks', service_id])

    def node(self, node_id):
        """Return the health info for a given node.

        :param str node_id: The node ID
        :rtype: list

        """
        return self._get_list(['node', node_id])

    def service(self, service_id):
        """Returns the nodes and health info of a service

        :param str service_id: The service ID
        :rtype: list

        """
        return self._get_list(['service', service_id])

    def state(self, state):
        """Returns the checks in a given state where state is one of
        "unknown", "passing", "warning", or "critical".

        :param str state: The state to get checks for
        :rtype: list

        """
        return self._get_list(['state', state])


class Status(_Endpoint):
    """Get information about the status of the Consul cluster. This are
    generally very low level, and not really useful for clients.

    """
    def leader(self):
        """Get the Raft leader for the datacenter the agent is running in.

        :rtype: str

        """
        self._get(['leader'])

    def peers(self):
        """Get the Raft peers for the datacenter the agent is running in.

        :rtype: list

        """
        self._get(['peers'])

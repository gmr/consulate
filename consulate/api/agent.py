"""
Consul Agent Endpoint Access

"""
from consulate.api import base


class Agent(base.Endpoint):
    """The Consul agent is the core process of Consul. The agent maintains
    membership information, registers services, runs checks, responds to
    queries and more. The agent must run on every node that is part of a
    Consul cluster.

    """
    def __init__(self, uri, adapter, datacenter=None, token=None):
        """Create a new instance of the Agent class

        :param str uri: Base URI
        :param consul.adapters.Request adapter: Request adapter
        :param str datacenter: datacenter
        :param str token: Access Token

        """
        super(Agent, self).__init__(uri, adapter, datacenter, token)
        self.check = Agent.Check(self._base_uri, adapter, datacenter, token)
        self.service = Agent.Service(self._base_uri, adapter,
                                     datacenter, token)

    class Check(base.Endpoint):
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
        def register(self, name, script=None, check_id=None, interval=None,
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

    class Service(base.Endpoint):
        """One of the main goals of service discovery is to provide a catalog
        of available services. To that end, the agent provides a simple
        service definition format to declare the availability of a service, a
        nd to potentially associate it with a health check. A health check is
        considered to be application level if it associated with a service. A
        service is defined in a configuration file, or added at runtime over
        the HTTP interface.

        """
        CHECK_EXCEPTION = 'check must be a tuple of script, interval, and ttl'

        def register(self, name, service_id=None, address=None, port=None,
                     tags=None, check=None, interval=None, ttl=None):
            """Add a new service to the local agent.

            :param str name: The name of the service
            :param str service_id: The id for the service (optional)
            :param str address: The service IP address
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
                       'address': address,
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

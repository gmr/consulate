"""
Consul Agent Endpoint Access

"""
from consulate.api import base
from consulate.models import agent as models

_TOKENS = [
    'acl_token',
    'acl_agent_token',
    'acl_agent_master_token',
    'acl_replication_token'
]


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
        self.service = Agent.Service(
            self._base_uri, adapter, datacenter, token)

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

        def register(self,
                     name,
                     check_id=None,
                     interval=None,
                     notes=None,
                     deregister_critical_service_after=None,
                     args=None,
                     docker_container_id=None,
                     grpc=None,
                     grpc_use_tls=None,
                     http=None,
                     http_method=None,
                     header=None,
                     timeout=None,
                     tls_skip_verify=None,
                     tcp=None,
                     ttl=None,
                     service_id=None,
                     status=None):
            """Add a new check to the local agent. Checks are either a script
            or TTL type. The agent is responsible for managing the status of
            the check and keeping the Catalog in sync.

            :param str name:
            :param str check_id:
            :param str interval:
            :param str notes:
            :param str deregister_critical_service_after:
            :param str args:
            :param str docker_container_id:
            :param str grpc:
            :param str grpc_use_tls:
            :param str http:
            :param str http_method:
            :param str header:
            :param str timeout:
            :param str tls_skip_verify:
            :param str tcp:
            :param str ttl:
            :param str service_id:
            :param str status:

            :rtype: bool
            :raises: ValueError

            """
            return self._put_no_response_body(
                ['register'], None, dict(
                    models.Check(
                        name=name,
                        id=check_id,
                        interval=interval,
                        notes=notes,
                        deregister_critical_service_after=
                        deregister_critical_service_after,
                        args=args,
                        docker_container_id=docker_container_id,
                        grpc=grpc,
                        grpc_use_tls=grpc_use_tls,
                        http=http,
                        method=http_method,
                        header=header,
                        timeout=timeout,
                        tls_skip_verify=tls_skip_verify,
                        tcp=tcp,
                        ttl=ttl,
                        service_id=service_id,
                        status=status)))

        def deregister(self, check_id):
            """Remove a check from the local agent. The agent will take care
            of deregistering the check with the Catalog.

            :param str check_id: The check id
            :rtype: bool

            """
            return self._put_no_response_body(['deregister', check_id])

        def ttl_pass(self, check_id, note=None):
            """This endpoint is used with a check that is of the TTL type.
            When this endpoint is accessed, the status of the check is set to
            "passing", and the TTL clock is reset.

            :param str check_id: The check id
            :param str note: Note to include with the check pass
            :rtype: bool

            """
            return self._put_no_response_body(
                ['pass', check_id], {'note': note} if note else None)

        def ttl_warn(self, check_id, note=None):
            """This endpoint is used with a check that is of the TTL type.
            When this endpoint is accessed, the status of the check is set
            to "warning", and the TTL clock is reset.

            :param str check_id: The check id
            :param str note: Note to include with the check warning
            :rtype: bool

            """
            return self._put_no_response_body(
                ['warn', check_id], {'note': note} if note else None)

        def ttl_fail(self, check_id, note=None):
            """This endpoint is used with a check that is of the TTL type.
            When this endpoint is accessed, the status of the check is set
            to "critical", and the TTL clock is reset.

            :param str check_id: The check id
            :param str note: Note to include with the check failure
            :rtype: bool

            """
            return self._put_no_response_body(
                ['fail', check_id], {'note': note} if note else None)

    class Service(base.Endpoint):
        """One of the main goals of service discovery is to provide a catalog
        of available services. To that end, the agent provides a simple
        service definition format to declare the availability of a service, a
        nd to potentially associate it with a health check. A health check is
        considered to be application level if it associated with a service. A
        service is defined in a configuration file, or added at runtime over
        the HTTP interface.

        """
        def register(self,
                     name,
                     service_id=None,
                     address=None,
                     port=None,
                     tags=None,
                     meta=None,
                     check=None,
                     checks=None,
                     enable_tag_override=None):
            """Add a new service to the local agent.

            :param str name: The name of the service
            :param str service_id: The id for the service (optional)
            :param str address: The service IP address
            :param int port: The service port
            :param list tags: A list of tags for the service
            :param list meta: A list of KV pairs for the service
            :param check: An optional check definition for the service
            :type check: :class:`consulate.models.agent.Check`
            :param checks: A list of check definitions for the service
            :type checks: list([:class:`consulate.models.agent.Check`])
            :param bool enable_tag_override: Toggle the tag override feature
            :rtype: bool
            :raises: ValueError

            """
            return self._put_no_response_body(
                ['register'], None,
                dict(models.Service(
                    name=name, id=service_id, address=address, port=port,
                    tags=tags, meta=meta, check=check, checks=checks,
                    enable_tag_override=enable_tag_override)))

        def deregister(self, service_id):
            """Deregister the service from the local agent. The agent will
            take care of deregistering the service with the Catalog. If there
            is an associated check, that is also deregistered.

            :param str service_id: The service id to deregister
            :rtype: bool

            """
            return self._put_no_response_body(['deregister', service_id])

        def maintenance(self, service_id, enable=True, reason=None):
            """Place given service into "maintenance mode".

            :param str service_id: The id for the service
            :param bool enable: Enable maintenance mode
            :param str reason: Reason for putting node in maintenance
            :rtype: bool

            """
            query_params = {'enable': enable}
            if reason:
                query_params['reason'] = reason
            return self._put_no_response_body(['maintenance', service_id],
                                              query_params)

    def checks(self):
        """Return the all the checks that are registered with the local agent.
        These checks were either provided through configuration files, or
        added dynamically using the HTTP API. It is important to note that
        the checks known by the agent may be different than those reported
        by the Catalog. This is usually due to changes being made while there
        is no leader elected. The agent performs active anti-entropy, so in
        most situations everything will be in sync within a few seconds.

        :rtype: dict

        """
        return self._get(['checks'])

    def force_leave(self, node):
        """Instructs the agent to force a node into the left state. If a node
        fails unexpectedly, then it will be in a "failed" state. Once in this
        state, Consul will attempt to reconnect, and additionally the services
        and checks belonging to that node will not be cleaned up. Forcing a
        node into the left state allows its old entries to be removed.

        """
        return self._put_no_response_body(['force-leave', node])

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
        return self._put_no_response_body(['join', address], query_params)

    def maintenance(self, enable=True, reason=None):
        """Places the agent into or removes the agent from "maintenance mode".

        .. versionadded:: 1.0.0

        :param bool enable: Enable or disable maintenance. Default: `True`
        :param str reason: The reason for the maintenance
        :rtype: bool

        """
        query_params = {'enable': enable}
        if reason:
            query_params['reason'] = reason
        return self._put_no_response_body(['maintenance'], query_params)

    def members(self):
        """Returns the members the agent sees in the cluster gossip pool.
        Due to the nature of gossip, this is eventually consistent and the
        results may differ by agent. The strongly consistent view of nodes
        is instead provided by ``Consulate.catalog.nodes``.

        :rtype: list

        """
        return self._get_list(['members'])

    def metrics(self):
        """Returns agent's metrics for the most recent finished interval

        .. versionadded:: 1.0.0

        :rtype: dict

        """
        return self._get(['metrics'])

    def monitor(self):
        """Iterator over logs from the local agent.

        .. versionadded:: 1.0.0

        :rtype: iterator

        """
        for line in self._get_stream(['monitor']):
            yield line

    def reload(self):
        """This endpoint instructs the agent to reload its configuration.
        Any errors encountered during this process are returned.

        .. versionadded:: 1.0.0

        :rtype: list

        """
        return self._put_response_body(['reload']) or None

    def services(self):
        """return the all the services that are registered with the local
        agent. These services were either provided through configuration
        files, or added dynamically using the HTTP API. It is important to
        note that the services known by the agent may be different than those
        ]reported by the Catalog. This is usually due to changes being made
        while there is no leader elected. The agent performs active
        anti-entropy, so in most situations everything will be in sync
        within a few seconds.

        :rtype: dict

        """
        return self._get(['services'])

    def self(self):
        """ This endpoint is used to return the configuration and member
        information of the local agent under the Config key.

        :rtype: dict

        """
        return self._get(['self'])

    def token(self, name, value):
        """Update the ACL tokens currently in use by the agent. It can be used
        to introduce ACL tokens to the agent for the first time, or to update
        tokens that were initially loaded from the agent's configuration.
        Tokens are not persisted, so will need to be updated again if the agent
        is restarted.

        Valid names:

          - ``acl_token``
          - ``acl_agent_token``
          - ``acl_agent_master_token``
          - ``acl_replication_token``

        .. versionadded:: 1.0.0

        :param str name: One of the valid token names.
        :param str value: The new token value
        :rtype: bool
        :raises: ValueError

        """
        if name not in _TOKENS:
            raise ValueError('Invalid token name: {}'.format(name))
        return self._put_no_response_body(
            ['token', name], {}, {'Token': value})

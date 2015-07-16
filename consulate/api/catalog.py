"""
Consul Catalog Endpoint Access

"""
from consulate.api import base


class Catalog(base.Endpoint):
    """The Consul agent is the core process of Consul. The agent maintains
    membership information, registers services, runs checks, responds to
    queries and more. The agent must run on every node that is part of a
    Consul cluster.

    """

    def __init__(self, uri, adapter, dc=None, token=None):
        super(Catalog, self).__init__(uri, adapter, dc, token)

    def register(self, node, address,
                 datacenter=None,
                 service=None,
                 check=None):
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

        return self._adapter.put(['register'], payload)

    def deregister(self, node, datacenter=None, check_id=None, service_id=None):
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
        return self._adapter.put(['deregister'], payload)

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

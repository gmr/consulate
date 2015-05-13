"""
Consul Health Endpoint Access

"""
from consulate.api import base


class Health(base.Endpoint):
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

    def service(self, service_id, tag=None, passing=None):
        """Returns the nodes and health info of a service

        :param str service_id: The service ID
        :rtype: list

        """

        query_params = {}
        if tag:
            query_params['tag'] = tag
        if passing:
            query_params['passing'] = ''

        return self._get_list(['service', service_id],
                              query_params=query_params)

    def state(self, state):
        """Returns the checks in a given state where state is one of
        "unknown", "passing", "warning", or "critical".

        :param str state: The state to get checks for
        :rtype: list

        """
        return self._get_list(['state', state])

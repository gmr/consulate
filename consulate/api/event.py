"""
Consul Event Endpoint Access

"""
from consulate.api import base


class Event(base.Endpoint):
    """The Event endpoints are used to fire a new event and list recent events.

    """

    def fire(self, name,
             payload=None,
             datacenter=None,
             node=None,
             service=None,
             tag=None):
        """Trigger a new user Event

        :param str name: The name of the event
        :param str payload: The opaque event payload
        :param str datacenter: Optional datacenter to fire the event in
        :param str node: Optional node to fire the event for
        :param str service: Optional service to fire the event for
        :param str tag: Option tag to fire the event for
        :return str: the new event ID

        """
        query_args = {}
        if datacenter:
            query_args['dc'] = datacenter
        if node:
            query_args['node'] = node
        if service:
            query_args['service'] = service
        if tag:
            query_args['tag'] = tag
        response = self._adapter.put(self._build_uri(['fire', name],
                                                     query_args), payload)
        return response.body.get('ID')

    def list(self, name=None):
        """Returns the most recent events known by the agent. As a consequence
        of how the event command works, each agent may have a different view of
        the events. Events are broadcast using the gossip protocol, so they
        have no global ordering nor do they make a promise of delivery.

        :return: list

        """
        query_args = {}
        if name:
            query_args['name'] = name
        return self._get(['list'], query_args)

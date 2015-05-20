"""
Consul Status Endpoint Access

"""
from consulate.api import base


class Status(base.Endpoint):
    """Get information about the status of the Consul cluster. This are
    generally very low level, and not really useful for clients.

    """

    def leader(self):
        """Get the Raft leader for the datacenter the agent is running in.

        :rtype: str

        """
        return self._get(['leader'])

    def peers(self):
        """Get the Raft peers for the datacenter the agent is running in.

        :rtype: list

        """
        value = self._get(['peers'])
        if not isinstance(value, list):
            return [value]
        return value

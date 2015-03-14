"""
Consul ACL Endpoint Access

"""
from consulate.api import base


class ACL(base.Endpoint):
    """The ACL endpoints are used to create, update, destroy, and query ACL
    tokens.

    """
    def create(self, name, acl_type='client', rules=None):
        """The create endpoint is used to make a new token. A token has a name,
        a type, and a set of ACL rules.

        The ``name`` property is opaque to Consul. To aid human operators, it
        should be a meaningful indicator of the ACL's purpose.

        ``acl_type`` is either client or management. A management token is
        comparable to a root user and has the ability to perform any action
        including creating, modifying, and deleting ACLs.

        By contrast, a client token can only perform actions as permitted by
        the rules associated. Client tokens can never manage ACLs. Given this
        limitation, only a management token can be used to make requests to
        the create endpoint.

        ``rules`` is a HCL string defining the rule policy. See
        `https://consul.io/docs/internals/acl.html`_ for more information on
        defining rules.

        The call to create will return the ID of the new ACL.

        :param str name: The name of the ACL to create
        :param str acl_type: One of "client" or "management"
        :param str rules: The rules HCL string
        :rtype: str

        """
        payload = {'Name': name, 'Type': acl_type}
        if rules:
            payload['Rules'] = rules
        response = self._adapter.put(self._build_uri(['create']), payload)
        return response.body.get('ID')

    def clone(self, acl_id):
        """Clone an existing ACL returning the new ACL ID

        :param str acl_id: The ACL id
        :rtype: bool

        """
        response = self._adapter.put(self._build_uri(['clone', acl_id]))
        return response.body.get('ID')

    def destroy(self, acl_id):
        """Delete the specified ACL

        :param str acl_id: The ACL id
        :rtype: bool

        """
        response = self._adapter.put(self._build_uri(['destroy', acl_id]))
        return response.status_code == 200

    def info(self, acl_id):
        """Return a dict of information about the ACL

        :param str acl_id: The ACL id
        :rtype: dict

        """
        return self._get(['info', acl_id])

    def list(self):
        """Return a list of all ACLs

        :rtype: list

        """
        return self._get(['list'])

    def update(self, acl_id, name, acl_type='client', rules=None):
        """Update an existing ACL, updating its values

        :param str acl_id: The ACL id
        :rtype: bool

        """
        payload = {'ID': acl_id, 'Name': name, 'Type': acl_type}
        if rules:
            payload['Rules'] = rules
        response = self._adapter.put(self._build_uri(['update']), payload)
        return response.status_code == 200

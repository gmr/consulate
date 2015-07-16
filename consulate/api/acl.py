"""
Consul ACL Endpoint Access

"""
from consulate.api import base
from consulate import exceptions


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
        :raises: consulate.exceptions.Forbidden

        """
        payload = {'Name': name, 'Type': acl_type}
        if rules:
            payload['Rules'] = rules
        response = self._adapter.put(self._build_uri(['create']), payload)
        if response.status_code == 403:
            raise exceptions.Forbidden(response.body)
        return response.body.get('ID')

    def clone(self, acl_id):
        """Clone an existing ACL returning the new ACL ID

        :param str acl_id: The ACL id
        :rtype: bool
        :raises: consulate.exceptions.Forbidden
        :raises: consulate.exceptions.NotFound

        """
        response = self._adapter.put(self._build_uri(['clone', acl_id]))
        # if response.status_code == 403:
        #     raise exceptions.Forbidden(response.body)
        if response.status_code == 404:
            raise exceptions.NotFound(response.body)
        return response.body.get('ID')

    def destroy(self, acl_id):
        """Delete the specified ACL

        :param str acl_id: The ACL id
        :rtype: bool
        :raises: consulate.exceptions.Forbidden
        :raises: consulate.exceptions.NotFound

        """
        response = self._adapter.put(self._build_uri(['destroy', acl_id]))
        if response.status_code == 403:
            raise exceptions.Forbidden(response.body)
        # elif response.status_code == 404:
        #     raise exceptions.NotFound(response.body)
        return response.status_code == 200

    def info(self, acl_id):
        """Return a dict of information about the ACL

        :param str acl_id: The ACL id
        :rtype: dict
        :raises: consulate.exceptions.Forbidden
        :raises: consulate.exceptions.NotFound

        """
        result = self._get(['info', acl_id], raise_on_404=True)
        if result is None:
            raise exceptions.NotFound()
        return result

    def list(self):
        """Return a list of all ACLs

        :rtype: list
        :raises: consulate.exceptions.Forbidden

        """
        return self._get(['list'])

    def update(self, acl_id, name, acl_type='client', rules=None):
        """Update an existing ACL, updating its values or add a new ACL if
        the ACL Id specified is not found.

        :param str acl_id: The ACL id
        :rtype: bool
        :raises: consulate.exceptions.Forbidden

        """
        payload = {'ID': acl_id, 'Name': name, 'Type': acl_type}
        if rules:
            payload['Rules'] = rules
        response = self._adapter.put(self._build_uri(['update']), payload)
        if response.status_code == 403:
            raise exceptions.Forbidden(response.body)
        return response.status_code == 200

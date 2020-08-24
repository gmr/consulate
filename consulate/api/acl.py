"""
Consul ACL Endpoint Access

"""
import logging

from consulate.models import acl as model
from consulate.api import base
from consulate import exceptions
# from typing import List, Dict, Union

LOGGER = logging.getLogger(__name__)

# ServiceIdentity = Dict[str, Union[str, List[str]]]
# ServiceIdentities = List[ServiceIdentity]
# PolicyLink = Dict[str, str]
# PolicyLinks = List[PolicyLink]
# RoleLink = Dict[str, str]
# RoleLinks = List[RoleLink]


class ACL(base.Endpoint):
    """The ACL endpoints are used to create, update, destroy, and query ACL
    tokens.

    """
    def list_policies(self):
        """List all ACL policies available in cluster.

        :param rtype: list

        """
        return self._get(["policies"])

    def read_policy(self, id):
        """Read an existing policy with the given ID.

        :param str id: The ID of the policy.
        :param rtype: dict

        """
        return self._get(["policy", id])

    def create_policy(self,
                      name,
                      datacenters=None,
                      description=None,
                      rules=None):
        """Create policy with name given and rules.

        :param str name: name of the policy
        :param list() datacenters: A list of datacenters to filter on policy.
        :param str description: Human readable description of the policy.
        :param str rules: A json serializable string for ACL rules.
        :param rtype: dict

        """
        return self._put_response_body(["policy"], {},
                                       dict(
                                           model.ACLPolicy(
                                               name=name,
                                               datacenters=datacenters,
                                               description=description,
                                               rules=rules)))

    def update_policy(self,
                      id,
                      name,
                      datacenters=None,
                      description=None,
                      rules=None):
        """Update policy with id given.

        :param str id: A UUID for the policy to update.
        :param str name: name of the policy
        :param list() datacenters: A list of datacenters to filter on policy.
        :param str description: Human readable description of the policy.
        :param str rules: A json serializable string for ACL rules.
        :param rtype: dict

        """
        return self._put_response_body(["policy", id], {},
                                       dict(
                                           model.ACLPolicy(
                                               name=name,
                                               datacenters=datacenters,
                                               description=description,
                                               rules=rules)))

    def delete_policy(self, id):
        """Delete an existing policy with the given ID.

        :param str id: The ID of the policy.
        :param rtype: bool

        """
        return self._delete(["policy", id])

    def list_roles(self):
        """List all ACL roles available in cluster
        :param rtype: list

        """
        return self._get(["roles"])

    def read_role(self, id=None, name=None):
        """Read an existing role with the given ID or Name.

        :param str id: The ID of the role.
        :param str name: The name of the role.
        :param rtype: dict

        """
        if id is not None:
            return self._get(["role", id])
        elif name is not None:
            return self._get(["role", "name", name])
        else:
            raise exceptions.NotFound("Either id or name must be specified")

    def create_role(self,
                    name,
                    description=None,
                    policies=None,
                    service_identities=None):
        """Create an ACL role from a list of policies or service identities.

        :param str name: The name of the ACL role. Must be unique.
        :param str description: The description of the ACL role.
        :param PolicyLinks policies: An array of PolicyLink.
        :param ServiceIdentities service_identities: A ServiceIdentity array.
        :param rtype: dict

        """
        return self._put_response_body(
            ["role"], {},
            dict(
                model.ACLRole(name=name,
                              description=description,
                              policies=policies,
                              service_identities=service_identities)))

    def update_role(self,
                    id,
                    name,
                    description=None,
                    policies=None,
                    service_identities=None):
        """Update role with id given.

        :param str id: A UUID for the policy to update.
        :param str name: name of the policy
        :param list() datacenters: A list of datacenters to filter on policy.
        :param str description: Human readable description of the policy.
        :param str rules: A json serializable string for ACL rules.
        :param rtype: dict

        """
        return self._put_response_body(
            ["role", id], {},
            dict(
                model.ACLRole(name=name,
                              description=description,
                              policies=policies,
                              service_identities=service_identities)))

    def delete_role(self, id):
        """Delete an existing role with the given ID.

        :param str id: The ID of the role.
        :param rtype: bool

        """
        return self._delete(["policy", id])

    def list_tokens(self):
        """List all ACL tokens available in cluster.

        :param rtype: list

        """
        return self._get(["tokens"])

    def read_token(self, accessor_id):
        """Read an existing token with the given ID.

        :param str id: The ID of the role.
        :param rtype: dict

        """
        return self._get(["token", accessor_id])

    def read_self_token(self):
        """Retrieve the currently used token.

        :param rtype: dict

        """
        return self._get(["token", "self"])

    def create_token(self,
                     accessor_id=None,
                     description=None,
                     expiration_time=None,
                     expiration_ttl=None,
                     local=False,
                     policies=None,
                     roles=None,
                     secret_id=None,
                     service_identities=None):
        """Create a token from the roles, policies, and service identities
        provided.

        :param str accessor_id: A UUID for accessing the token.
        :param str description: A human-readable description of the token.
        :param str expiration_time: The amount of time till the token expires.
        :param str expiration_ttl: Sets expiration_time to creation time +
        expiration_ttl value.
        :param bool local: Whether the token is only locally available in the
        current datacenter or to all datacenters defined.
        :param PolicyLinks policies: A PolicyLink array.
        :param RoleLinks roles: A RoleLink array.
        :param str secret_id: A UUID for making requests to consul.
        :param ServiceIdentities service_identities: A ServiceIdentity array.
        :param rtype: dict

        """
        return self._put_response_body(
            ["token"], {},
            dict(
                model.ACLToken(accessor_id=accessor_id,
                               description=description,
                               expiration_time=expiration_time,
                               expiration_ttl=expiration_ttl,
                               local=local,
                               policies=policies,
                               roles=roles,
                               secret_id=secret_id,
                               service_identities=service_identities)))

    def update_token(self,
                     accessor_id,
                     description=None,
                     expiration_time=None,
                     expiration_ttl=None,
                     local=False,
                     policies=None,
                     roles=None,
                     secret_id=None,
                     service_identities=None):
        """Create a token from the roles, policies, and service identities
        provided.

        :param str accessor_id: A UUID for accessing the token.
        :param str description: A human-readable description of the token.
        :param str expiration_time: The amount of time till the token expires.
        :param str expiration_ttl: Sets expiration_time to creation time +
        expiration_ttl value.
        :param bool local: Whether the token is only locally available in the
        current datacenter or to all datacenters defined.
        :param PolicyLinks policies: A PolicyLink array.
        :param RoleLinks roles: A RoleLink array.
        :param str secret_id: A UUID for making requests to consul.
        :param ServiceIdentities service_identities: A ServiceIdentity array.
        :param rtype: dict

        """
        return self._put_response_body(
            ["token", accessor_id], {},
            dict(
                model.ACLToken(accessor_id=accessor_id,
                               description=description,
                               expiration_time=expiration_time,
                               expiration_ttl=expiration_ttl,
                               local=local,
                               policies=policies,
                               roles=roles,
                               secret_id=secret_id,
                               service_identities=service_identities)))

    def clone_token(self, accessor_id, description=None):
        """Clone a token by the accessor_id.

        :param str accessor_id: A UUID for accessing the token.
        :param str description: A human-readable description of the token.
        :param rtype: dict

        """
        return self._put_response_body(
            ["token", accessor_id, "clone"], {},
            dict(model.ACLToken(description=description)))

    def delete_token(self, accessor_id):
        """Delete an existing token with the given AcccessorID.

        :param str id: The AccessorID of the token.
        :param rtype: bool

        """
        return self._delete(["token", accessor_id])

    # NOTE: Everything below here is deprecated post consul-1.4.0.

    def bootstrap(self):
        """This endpoint does a special one-time bootstrap of the ACL system,
        making the first management token if the acl_master_token is not
        specified in the Consul server configuration, and if the cluster has
        not been bootstrapped previously.

        This is available in Consul 0.9.1  and later, and requires all Consul
        servers to be upgraded in order to operate.

        You can detect if something has interfered with the ACL bootstrapping
        by the response of this method. If you get a string response with the
        ``ID``, the bootstrap was a success. If the method raises a
        :exc:`~consulate.exceptions.Forbidden` exception, the cluster has
        already been bootstrapped, at which point you should consider the
        cluster in a potentially compromised state.

        .. versionadded: 1.0.0

        :rtype: str
        :raises: :exc:`~consulate.exceptions.Forbidden`

        """
        return self._put_response_body(['bootstrap'])['ID']

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
        `Internals on <https://www.consul.io/docs/internals/acl.html>`_ ACL
        for more information on defining rules.

        The call to create will return the ID of the new ACL.

        :param str name: The name of the ACL to create
        :param str acl_type: One of "client" or "management"
        :param str rules: The rules HCL string
        :rtype: str
        :raises: consulate.exceptions.Forbidden

        """
        return self._put_response_body(['create'], {},
                                       dict(
                                           model.ACL(name=name,
                                                     type=acl_type,
                                                     rules=rules)))['ID']

    def clone(self, acl_id):
        """Clone an existing ACL returning the new ACL ID

        :param str acl_id: The ACL id
        :rtype: bool
        :raises: consulate.exceptions.Forbidden

        """
        return self._put_response_body(['clone', acl_id])['ID']

    def destroy(self, acl_id):
        """Delete the specified ACL

        :param str acl_id: The ACL id
        :rtype: bool
        :raises: consulate.exceptions.Forbidden

        """
        response = self._adapter.put(self._build_uri(['destroy', acl_id]))
        if response.status_code == 403:
            raise exceptions.Forbidden(response.body)
        return response.status_code == 200

    def info(self, acl_id):
        """Return a dict of information about the ACL

        :param str acl_id: The ACL id
        :rtype: dict
        :raises: consulate.exceptions.Forbidden
        :raises: consulate.exceptions.NotFound

        """
        response = self._get(['info', acl_id], raise_on_404=True)
        if not response:
            raise exceptions.NotFound('ACL not found')
        return response

    def list(self):
        """Return a list of all ACLs

        :rtype: list([dict])
        :raises: consulate.exceptions.Forbidden

        """
        return self._get(['list'])

    def replication(self):
        """Return the status of the ACL replication process in the datacenter.

        This is intended to be used by operators, or by automation checking the
        health of ACL replication.

        .. versionadded: 1.0.0

        :rtype: dict
        :raises: consulate.exceptions.Forbidden

        """
        return self._get(['replication'])

    def update(self, acl_id, name, acl_type='client', rules=None):
        """Update an existing ACL, updating its values or add a new ACL if
        the ACL ID specified is not found.

        The call will return the ID of the ACL.

        :param str acl_id: The ACL id
        :param str name: The name of the ACL
        :param str acl_type: The ACL type
        :param str rules: The ACL rules document
        :rtype: str
        :raises: consulate.exceptions.Forbidden

        """
        return self._put_response_body(['update'], {},
                                       dict(
                                           model.ACL(id=acl_id,
                                                     name=name,
                                                     type=acl_type,
                                                     rules=rules)))['ID']

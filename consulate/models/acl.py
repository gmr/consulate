# coding=utf-8
"""Models for the ACL endpoints"""
import uuid

from consulate.models import base


def _validate_link_array(value, model):
    """ Validate the policies or roles links are formatted correctly.

    :param list value: An array of PolicyLink or RoleLink.
    :param rtype: bool

    """
    return all(['ID' in link or 'Name' in link for link in value])


def _validate_service_identities(value, model):
    """ Validate service_identities is formatted correctly.

    :param ServiceIdentities value: A ServiceIdentity list
    :param rtype: bool

    """
    return all(
        ['ServiceName' in service_identity for service_identity in value])


class ACLPolicy(base.Model):
    """Defines the model used for an ACL policy."""
    __slots__ = ['datacenters', 'description', 'id', 'name', 'rules']

    __attributes__ = {
        'datacenters': {
            'key': 'Datacenters',
            'type': list,
        },
        'description': {
            'key': 'Description',
            'type': str,
        },
        'id': {
            'key': 'ID',
            'type': uuid.UUID,
            'cast_from': str,
            'cast_to': str,
        },
        'name': {
            'key': 'Name',
            'type': str,
        },
        'rules': {
            'key': 'Rules',
            'type': str,
        }
    }


class ACLRole(base.Model):
    """Defines the model used for an ACL role."""
    __slots__ = ['description', 'name', 'policies', 'service_identities']

    __attributes__ = {
        'description': {
            'key': 'Description',
            'type': str,
        },
        'name': {
            'key': 'Name',
            'type': str,
            'required': True,
        },
        'policies': {
            'key': 'Policies',
            'type': list,
            'validator': _validate_link_array,
        },
        "service_identities": {
            'key': 'ServiceIdentities',
            'type': list,
            'validator': _validate_service_identities,
        }
    }


class ACLToken(base.Model):
    """Defines the model used for an ACL token."""
    __slots__ = [
        'accessor_id', 'description', 'expiration_time', 'expiration_ttl',
        'local', 'policies', 'roles', 'secret_id', 'service_identities'
    ]

    __attributes__ = {
        'accessor_id': {
            'key': 'AccessorID',
            'type': uuid.UUID,
            'cast_from': str,
            'cast_to': str,
        },
        'description': {
            'key': 'Description',
            'type': str,
        },
        'expiration_time': {
            'key': 'ExpirationTime',
            'type': str,
        },
        'expiration_ttl': {
            'key': 'ExpirationTTL',
            'type': str,
        },
        'local': {
            'key': 'Local',
            'type': bool,
        },
        'policies': {
            'key': 'Policies',
            'type': list,
            'validator': _validate_link_array,
        },
        'roles': {
            'key': 'Roles',
            'type': list,
            'validator': _validate_link_array,
        },
        'secret_id': {
            'key': 'SecretID',
            'type': uuid.UUID,
            'cast_from': str,
            'cast_to': str,
        },
        "service_identities": {
            'key': 'ServiceIdentities',
            'type': list,
            'validator': _validate_service_identities,
        }
    }


# NOTE: Everything below here is deprecated post consul-1.4.0.


class ACL(base.Model):
    """Defines the model used for an individual ACL token."""
    __slots__ = ['id', 'name', 'type', 'rules']

    __attributes__ = {
        'id': {
            'key': 'ID',
            'type': uuid.UUID,
            'cast_from': str,
            'cast_to': str
        },
        'name': {
            'key': 'Name',
            'type': str
        },
        'type': {
            'key': 'Type',
            'type': str,
            'enum': {'client', 'management'},
            'required': True
        },
        'rules': {
            'key': 'Rules',
            'type': str
        }
    }

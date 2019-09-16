# coding=utf-8
"""Models for the ACL endpoints"""
import uuid

from consulate.models import base


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
        },
        "service_identities": {
            'key': 'ServiceIdentities',
            'type': list,
        }
    }


class ACLToken(base.Model):
    """Defines the model used for an ACL token."""
    __slots__ = [
        'accessor_id', 'description', 'expiration_time', 'expiration_ttl',
        'local', 'policies', 'roles', 'secret_id', 'service_identities'
    ]
    pass


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

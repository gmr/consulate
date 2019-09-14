# coding=utf-8
"""Models for the ACL endpoints"""
import uuid

from consulate.models import base


class ACLPolicy(base.Model):
    """Defines the model used fur an ACL policy."""
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
    """Defines the model used fur an ACL role."""
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

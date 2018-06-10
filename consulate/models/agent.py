# coding=utf-8
"""Models for the Agent endpoints"""
from consulate.models import base
from consulate import utils


def _validate_args(value, model):
    """Validate that the args values are all strings and that it does not
    conflict with other attributes.

    :param list([str]) value: The args value
    :param consulate.models.agent.Check model: The model instance.
    :rtype: bool

    """
    return all([isinstance(v, str) for v in value]) \
        and not model.args and not model.grpc and not model.http \
        and not model.ttl


def _validate_grpc(value, model):
    """Validate that the HTTP value is a URL and that it does not conflict
    with other attributes.

    :param str value: The URL value
    :param consulate.models.agent.Check model: The model instance.
    :rtype: bool

    """
    return utils.validate_url(value) \
        and not model.args and not model.http \
        and not model.tcp and not model.ttl


def _validate_http(value, model):
    """Validate that the HTTP value is a URL and that it does not conflict
    with other attributes.

    :param str value: The URL value
    :param consulate.models.agent.Check model: The model instance.
    :rtype: bool

    """
    return utils.validate_url(value) \
        and not model.args and not model.grpc and not model.tcp \
        and not model.ttl


def _validate_interval(value, model):
    """Validate that interval does not conflict with other attributes.

    :param str value: The interval value
    :param consulate.models.agent.Check model: The model instance.
    :rtype: bool

    """
    return utils.validate_go_interval(value) and not model.ttl


def _validate_tcp(_value, model):
    """Validate that the TCP does not conflict with other attributes.

    :param str _value: The TCP value
    :param consulate.models.agent.Check model: The model instance.
    :rtype: bool

    """
    return not model.args and not model.grpc \
        and not model.http and not model.ttl


def _validate_ttl(value, model):
    """Validate that the TTL does not conflict with other attributes.

    :param str value: The TTL value
    :param consulate.models.agent.Check model: The model instance.
    :rtype: bool

    """
    return utils.validate_go_interval(value) and not model.args \
        and not model.grpc and not model.http \
        and not model.tcp and not model.interval


class Check(base.Model):
    """Model for making Check API requests to Consul."""

    __slots__ = ['id', 'name', 'interval', 'notes',
                 'deregister_critical_service_after', 'args',
                 'docker_container_id', 'grpc', 'grpc_use_tls',
                 'http', 'method', 'header', 'timeout', 'tls_skip_verify',
                 'tcp', 'ttl', 'service_id', 'status']

    __attributes__ = {
        'id': {
            'key': 'ID',
            'type': str
        },
        'name': {
            'key': 'Name',
            'type': str,
            'required': True
        },
        'interval': {
            'key': 'Interval',
            'type': str,
            'validator': _validate_interval
        },
        'notes': {
            'key': 'Notes',
            'type': str
        },
        'deregister_critical_service_after': {
            'key': 'DeregisterCriticalServiceAfter',
            'type': str,
            'validator': utils.validate_go_interval
        },
        'args': {
            'key': 'Args',
            'type': list,
            'validator': _validate_args
        },
        'docker_container_id': {
            'key': 'DockerContainerID',
            'type': str
        },
        'grpc': {
            'key': 'GRPC',
            'type': str,
            'validator': _validate_grpc
        },
        'grpc_use_tls': {
            'key': 'GRPCUseTLS',
            'type': bool
        },
        'http': {
            'key': 'HTTP',
            'type': str,
            'validator': _validate_http
        },
        'method': {
            'key': 'Method',
            'type': str,
            'enum': {
                'HEAD', 'GET', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'TRACE'
            }
        },
        'header': {
            'key': 'Header',
            'type': dict,
            'validator': lambda h, _m: all(
                [(isinstance(k, str) and isinstance(v, str))
                 for k, v in h.items()]),
            'cast_to': lambda h: {k: [v] for k, v in h.items()}
        },
        'timeout': {
            'key': 'Timeout',
            'type': str,
            'validator': utils.validate_go_interval
        },
        'tls_skip_verify': {
            'key': 'TLSSkipVerify',
            'type': bool
        },
        'tcp': {
            'key': 'TCP',
            'type': str,
            'validator': _validate_tcp
        },
        'ttl': {
            'key': 'TTL',
            'type': str,
            'validator': _validate_ttl
        },
        'service_id': {
            'key': 'ServiceID',
            'type': str
        },
        'status': {
            'key': 'Status',
            'type': str,
            'enum': {'passing', 'warning', 'critical', 'maintenance'}
        }
    }

    def __init__(self, **kwargs):
        super(Check, self).__init__(**kwargs)
        if (self.args or self.grpc or self.http or self.tcp) \
                and not self.interval:
            raise ValueError('"interval" must be specified when specifying '
                             'args, grpc, http, or tcp.')


class Service(base.Model):
    """Model for making Check API requests to Consul."""

    __slots__ = ['id', 'name', 'tags', 'meta', 'address', 'port', 'check',
                 'checks', 'enable_tag_override']

    __attributes__ = {
        'id': {
            'key': 'ID',
            'type': str
        },
        'name': {
            'key': 'Name',
            'type': str,
            'required': True
        },
        'tags': {
            'key': 'Tags',
            'type': list,
            'validator': lambda t, _m: all([isinstance(v, str) for v in t])
        },
        'meta': {
            'key': 'Meta',
            'type': dict,
            'validator': lambda h, _m: all(
                [(isinstance(k, str) and isinstance(v, str))
                 for k, v in h.items()]),
        },
        'address': {
            'key': 'Address',
            'type': str
        },
        'port': {
            'key': 'Port',
            'type': int
        },
        'check': {
            'key': 'Check',
            'type': Check,
            'cast_to': dict
        },
        'checks': {
            'key': 'Checks',
            'type': list,
            'validator': lambda c, _m: all([isinstance(v, Check) for v in c]),
            'cast_to': lambda c: [dict(check) for check in c]
        },
        'enable_tag_override': {
            'Key': 'EnableTagOverride',
            'type': bool
        }
    }


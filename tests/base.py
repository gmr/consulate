import functools
import json
import os
import unittest
import uuid

import httmock

import consulate
from consulate import exceptions

with open('testing/consul.json', 'r') as handle:
    CONSUL_CONFIG = json.load(handle)


def generate_key(func):
    @functools.wraps(func)
    def _decorator(self, *args, **kwargs):
        key = str(uuid.uuid4())[0:8]
        self.used_keys.append(key)
        func(self, key)

    return _decorator


@httmock.all_requests
def raise_oserror(_url_unused, _request):
    raise OSError


class TestCase(unittest.TestCase):
    def setUp(self):
        self.consul = consulate.Consul(
            host=os.environ['CONSUL_HOST'],
            port=os.environ['CONSUL_PORT'],
            token=CONSUL_CONFIG['acl']['tokens']['master'])
        self.forbidden_consul = consulate.Consul(
            host=os.environ['CONSUL_HOST'],
            port=os.environ['CONSUL_PORT'],
            token=str(uuid.uuid4()))
        self.used_keys = list()

    def tearDown(self):
        for key in self.consul.kv.keys():
            self.consul.kv.delete(key)

        checks = self.consul.agent.checks()
        for name in checks:
            self.consul.agent.check.deregister(checks[name]['CheckID'])

        services = self.consul.agent.services()
        for name in services:
            self.consul.agent.service.deregister(services[name]['ID'])

        for acl in self.consul.acl.list_tokens():
            if acl['AccessorID'] == CONSUL_CONFIG['acl']['tokens']['master']:
                continue
            try:
                uuid.UUID(acl['AccessorID'])
                self.consul.acl.delete_token(acl['AccessorID'])
            except (ValueError, exceptions.ConsulateException):
                pass

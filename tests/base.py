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
            token=CONSUL_CONFIG['acl_master_token'])
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

        for acl in self.consul.acl.list():
            if acl['ID'] == CONSUL_CONFIG['acl_master_token']:
                continue
            try:
                uuid.UUID(acl['ID'])
                self.consul.acl.destroy(acl['ID'])
            except (ValueError, exceptions.ConsulateException):
                pass

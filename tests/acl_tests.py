"""
Tests for Consulate.acl

"""
import json
import uuid

import httmock

import consulate
from consulate import exceptions

from . import base

ACL_RULES = """key "" {
  policy = "read"
}
key "foo/" {
  policy = "write"
}
"""


class TestCase(base.TestCase):

    @staticmethod
    def uuidv4():
        return str(uuid.uuid4())

    def test_bootstrap_request_exception(self):

        @httmock.all_requests
        def response_content(_url_unused, _request):
            raise OSError

        with httmock.HTTMock(response_content):
            with self.assertRaises(exceptions.RequestError):
                self.consul.acl.bootstrap()

    def test_bootstrap_success(self):
        expectation = self.uuidv4()

        @httmock.all_requests
        def response_content(_url_unused, request):
            return httmock.response(
                200, json.dumps({'ID': expectation}), {}, None, 0, request)

        with httmock.HTTMock(response_content):
            result = self.consul.acl.bootstrap()

        self.assertEqual(result, expectation)

    def test_bootstrap_raises(self):
        with self.assertRaises(consulate.Forbidden):
            self.consul.acl.bootstrap()

    def test_clone_bad_acl_id(self):
        with self.assertRaises(consulate.Forbidden):
            self.consul.acl.clone(self.uuidv4())

    def test_clone_forbidden(self):
        with self.assertRaises(consulate.Forbidden):
            self.forbidden_consul.acl.clone(self.uuidv4())

    def test_create_and_destroy(self):
        acl_id = self.consul.acl.create(self.uuidv4())
        self.assertTrue(self.consul.acl.destroy(acl_id))

    def test_create_with_rules(self):
        acl_id = self.consul.acl.create(self.uuidv4(), rules=ACL_RULES)
        value = self.consul.acl.info(acl_id)
        self.assertEqual(value['Rules'], ACL_RULES)

    def test_create_and_info(self):
        acl_id = self.consul.acl.create(self.uuidv4())
        self.assertIsNotNone(acl_id)
        data = self.consul.acl.info(acl_id)
        self.assertIsNotNone(data)
        self.assertEqual(acl_id, data.get('ID'))

    def test_create_and_list(self):
        acl_id = self.consul.acl.create(self.uuidv4())
        data = self.consul.acl.list()
        self.assertIn(acl_id, [r.get('ID') for r in data])

    def test_create_and_clone(self):
        acl_id = self.consul.acl.create(self.uuidv4())
        clone_id = self.consul.acl.clone(acl_id)
        data = self.consul.acl.list()
        self.assertIn(clone_id, [r.get('ID') for r in data])

    def test_create_and_update(self):
        acl_id = str(self.consul.acl.create(self.uuidv4()))
        self.consul.acl.update(acl_id, 'Foo')
        data = self.consul.acl.list()
        self.assertIn('Foo', [r.get('Name') for r in data])
        self.assertIn(acl_id, [r.get('ID') for r in data])

    def test_create_forbidden(self):
        with self.assertRaises(consulate.Forbidden):
            self.forbidden_consul.acl.create(self.uuidv4())

    def test_destroy_forbidden(self):
        with self.assertRaises(consulate.Forbidden):
            self.forbidden_consul.acl.destroy(self.uuidv4())

    def test_info_acl_id_not_found(self):
        with self.assertRaises(consulate.NotFound):
            self.forbidden_consul.acl.info(self.uuidv4())

    def test_list_request_exception(self):
        with httmock.HTTMock(base.raise_oserror):
            with self.assertRaises(exceptions.RequestError):
                self.consul.acl.list()

    def test_replication(self):
        result = self.forbidden_consul.acl.replication()
        self.assertFalse(result['Enabled'])
        self.assertFalse(result['Running'])

    def test_update_not_found_adds_new_key(self):
        acl_id = self.consul.acl.update(self.uuidv4(), 'Foo2')
        data = self.consul.acl.list()
        self.assertIn('Foo2', [r.get('Name') for r in data])
        self.assertIn(acl_id, [r.get('ID') for r in data])

    def test_update_with_rules(self):
        acl_id = self.consul.acl.update(self.uuidv4(), name='test', rules=ACL_RULES)
        value = self.consul.acl.info(acl_id)
        self.assertEqual(value['Rules'], ACL_RULES)

    def test_update_forbidden(self):
        with self.assertRaises(consulate.Forbidden):
            self.forbidden_consul.acl.update(self.uuidv4(), name='test')

"""
Tests for Consulate.acl

"""
import json
import uuid

import consulate
import httmock

from . import base

ACL_RULES = """key "" {
  policy = "read"
}
key "foo/" {
  policy = "write"
}
"""


class TestCase(base.TestCase):
    def setUp(self):
        super(TestCase, self).setUp()
        self.acl_list = list()

    def tearDown(self):
        for acl_id in self.acl_list:
            self.consul.acl.destroy(acl_id)

    def test_bootstrap_success(self):
        expectation = str(uuid.uuid4())

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
        acl_id = str(uuid.uuid4())
        with self.assertRaises(consulate.Forbidden):
            self.forbidden_consul.acl.clone(acl_id)

    @base.generate_key
    def test_clone_forbidden(self, acl_id):
        with self.assertRaises(consulate.Forbidden):
            self.forbidden_consul.acl.clone(acl_id)

    @base.generate_key
    def test_create_and_destroy(self, acl_id):
        acl_id = self.consul.acl.create(acl_id)
        self.acl_list.append(acl_id)
        self.assertTrue(self.consul.acl.destroy(acl_id))

    @base.generate_key
    def test_create_with_rules(self, acl_id):
        acl_id = self.consul.acl.create(acl_id, rules=ACL_RULES)
        self.acl_list.append(acl_id)
        value = self.consul.acl.info(acl_id)
        self.assertEqual(value['Rules'], ACL_RULES)

    @base.generate_key
    def test_create_and_info(self, acl_id):
        acl_id = self.consul.acl.create(acl_id)
        self.acl_list.append(acl_id)
        self.assertIsNotNone(acl_id)
        data = self.consul.acl.info(acl_id)
        self.assertIsNotNone(data)
        self.assertEqual(acl_id, data.get('ID'))

    @base.generate_key
    def test_create_and_list(self, acl_id):
        acl_id = self.consul.acl.create(acl_id)
        self.acl_list.append(acl_id)
        data = self.consul.acl.list()
        self.assertIn(acl_id, [r.get('ID') for r in data])

    @base.generate_key
    def test_create_and_clone(self, acl_id):
        acl_id = self.consul.acl.create(acl_id)
        self.acl_list.append(acl_id)
        clone_id = self.consul.acl.clone(acl_id)
        self.acl_list.append(clone_id)
        data = self.consul.acl.list()
        self.assertIn(clone_id, [r.get('ID') for r in data])

    @base.generate_key
    def test_create_and_update(self, acl_id):
        acl_id = self.consul.acl.create(acl_id)
        self.acl_list.append(acl_id)
        self.consul.acl.update(acl_id, 'Foo')
        data = self.consul.acl.list()
        self.assertIn('Foo', [r.get('Name') for r in data])
        self.assertIn(acl_id, [r.get('ID') for r in data])

    @base.generate_key
    def test_create_forbidden(self, acl_id):
        with self.assertRaises(consulate.Forbidden):
            self.forbidden_consul.acl.create(acl_id)

    @base.generate_key
    def test_destroy_forbidden(self, acl_id):
        with self.assertRaises(consulate.Forbidden):
            self.forbidden_consul.acl.destroy(acl_id)

    def test_info_acl_id_not_found(self):
        acl_id = str(uuid.uuid4())
        with self.assertRaises(consulate.NotFound):
            self.forbidden_consul.acl.info(acl_id)

    def test_replication(self):
        result = self.forbidden_consul.acl.replication()
        self.assertFalse(result['Enabled'])
        self.assertFalse(result['Running'])

    @base.generate_key
    def test_update_not_found_adds_new_key(self, acl_id):
        self.assertTrue(self.consul.acl.update(acl_id, 'Foo2'))
        data = self.consul.acl.list()
        self.assertIn('Foo2', [r.get('Name') for r in data])
        self.assertIn(acl_id, [r.get('ID') for r in data])

    @base.generate_key
    def test_update_with_rules(self, acl_id):
        self.consul.acl.update(acl_id, name='test', rules=ACL_RULES)
        self.acl_list.append(acl_id)
        value = self.consul.acl.info(acl_id)
        self.assertEqual(value['Rules'], ACL_RULES)

    @base.generate_key
    def test_update_forbidden(self, acl_id):
        with self.assertRaises(consulate.Forbidden):
            self.forbidden_consul.acl.update(acl_id, name='test')

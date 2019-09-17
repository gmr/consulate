"""
Tests for Consulate.acl

"""
import json
import uuid

import httmock

import consulate
from consulate import exceptions

from . import base

ACL_OLD_RULES = """key "" {
  policy = "read"
}
key "foo/" {
  policy = "write"
}
"""

ACL_NEW_RULES = """key_prefix "" {
    policy = "read
}
key "foo/" {
    policy = "write"
}
"""

ACL_NEW_UPDATE_RULES = """key_prefix "" {
    policy = "deny"
}
key "foo/" {
    policy = "read"
}
"""

POLICYLINKS_SAMPLE = [
    dict(Name="policylink_sample"),
]

POLICYLINKS_UPDATE_SAMPLE = [
    dict(Name="policylink_sample"),
    dict(Name="policylink_update_sample")
]

SERVICE_IDENTITIES_SAMPLE = [dict(ServiceName="db", Datacenters=["dc1"])]

ROLELINKS_SAMPLE = [dict(Name="role_sample")]


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
            return httmock.response(200, json.dumps({'ID': expectation}), {},
                                    None, 0, request)

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
        acl_id = self.consul.acl.create(self.uuidv4(), rules=ACL_OLD_RULES)
        value = self.consul.acl.info(acl_id)
        self.assertEqual(value['Rules'], ACL_OLD_RULES)

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
        acl_id = self.consul.acl.update(self.uuidv4(),
                                        name='test',
                                        rules=ACL_OLD_RULES)
        value = self.consul.acl.info(acl_id)
        self.assertEqual(value['Rules'], ACL_OLD_RULES)

    def test_update_forbidden(self):
        with self.assertRaises(consulate.Forbidden):
            self.forbidden_consul.acl.update(self.uuidv4(), name='test')

    # NOTE: Everything above here is deprecated post consul-1.4.0

    def test_create_policy(self):
        result = self.consul.acl.create_policy("unittest_create_policy",
                                               rules=ACL_NEW_RULES)
        self.assertEqual(result['Rules'], ACL_NEW_RULES)

    def test_create_and_read_policy(self):
        value = self.consul.acl.create_policy("unittest_read_policy",
                                              rules=ACL_NEW_RULES)
        result = self.consul.acl.read_policy(value["ID"])
        self.assertEqual(result['Rules'], ACL_NEW_RULES)

    def test_create_and_update_policy(self):
        value = self.consul.acl.create_policy("unittest_read_policy",
                                              rules=ACL_NEW_RULES)
        result = self.consul.acl.update_policy(value["ID"],
                                               value["Name"],
                                               rules=ACL_NEW_UPDATE_RULES)
        self.assertGreater(result["ModifyIndex"], result["CreateIndex"])

    def test_create_and_delete_policy(self):
        value = self.consul.acl.create_policy("unittest_delete_policy",
                                              rules=ACL_NEW_RULES)
        result = self.consul.acl.delete_policy(value["ID"])
        self.assertTrue(result)

    def test_list_policy_exception(self):
        with httmock.HTTMock(base.raise_oserror):
            with self.assertRaises(exceptions.RequestError):
                self.consul.acl.list_policies()

    def test_create_role(self):
        result = self.consul.acl.create_role(
            "unittest_create_role",
            policies=POLICYLINKS_SAMPLE,
            service_identities=SERVICE_IDENTITIES_SAMPLE)
        self.assertEqual(result[0]['ID'], POLICYLINKS_SAMPLE[0]['ID'])

    def test_create_and_read_role(self):
        value = self.consul.acl.create_role(
            "unittest_read_role",
            policies=POLICYLINKS_SAMPLE,
            service_identities=SERVICE_IDENTITIES_SAMPLE)
        result = self.consul.acl.read_role(value["ID"])
        self.assertEqual(result['Policies'][0]['ID'],
                         POLICYLINKS_SAMPLE[0]["ID"])

    def test_create_and_update_role(self):
        value = self.consul.acl.create_role(
            "unittest_read_role",
            policies=POLICYLINKS_SAMPLE,
            service_identities=SERVICE_IDENTITIES_SAMPLE)
        result = self.consul.acl.update_role(
            value["ID"],
            "unittest_read_role",
            policies=POLICYLINKS_UPDATE_SAMPLE)
        self.assertGreater(result["ModifyIndex"], result["CreateIndex"])

    def test_create_and_delete_role(self):
        value = self.consul.acl.create_role(
            "unittest_delete_role",
            policies=POLICYLINKS_SAMPLE,
            service_identities=SERVICE_IDENTITIES_SAMPLE)
        result = self.consul.acl.delete_role(value["ID"])
        self.assertTrue(result)

    def test_list_roles_exception(self):
        with httmock.HTTMock(base.raise_oserror):
            with self.assertRaises(exceptions.RequestError):
                self.consul.acl.list_roles()

    def test_create_token(self):
        secret_id = self.uuidv4()
        accessor_id = self.uuidv4()
        result = self.consul.acl.create_token(
            accessor_id=accessor_id,
            secret_id=secret_id,
            roles=ROLELINKS_SAMPLE,
            policies=POLICYLINKS_SAMPLE,
            service_identities=SERVICE_IDENTITIES_SAMPLE)
        self.assertEqual(result['AccessorID'], accessor_id)
        self.assertEqual(result['SecretID'], secret_id)

    def test_create_and_read_token(self):
        secret_id = self.uuidv4()
        accessor_id = self.uuidv4()
        value = self.consul.acl.create_token(
            accessor_id=accessor_id,
            secret_id=secret_id,
            roles=ROLELINKS_SAMPLE,
            policies=POLICYLINKS_SAMPLE,
            service_identities=SERVICE_IDENTITIES_SAMPLE)
        result = self.consul.acl.read_token(value["AccessorID"])
        self.assertEqual(result['AccessorID'], accessor_id)

    def test_create_and_update_token(self):
        secret_id = self.uuidv4()
        accessor_id = self.uuidv4()
        value = self.consul.acl.create_token(
            accessor_id=accessor_id,
            secret_id=secret_id,
            roles=ROLELINKS_SAMPLE,
            policies=POLICYLINKS_SAMPLE,
            service_identities=SERVICE_IDENTITIES_SAMPLE)
        result = self.consul.acl.update_token(
            value["AccessorID"], policies=POLICYLINKS_UPDATE_SAMPLE)
        self.assertGreater(result["ModifyIndex"], result["CreateIndex"])

    def test_create_and_clone_token(self):
        secret_id = self.uuidv4()
        accessor_id = self.uuidv4()
        clone_description = "clone token of " + accessor_id
        value = self.consul.acl.create_token(
            accessor_id=accessor_id,
            secret_id=secret_id,
            roles=ROLELINKS_SAMPLE,
            policies=POLICYLINKS_SAMPLE,
            service_identities=SERVICE_IDENTITIES_SAMPLE)
        result = self.consul.acl.clone_token(value["AccessorID"],
                                             description="clone")
        self.assertEqual(result["Description"], clone_description)

    def test_create_and_delete_token(self):
        secret_id = self.uuidv4()
        accessor_id = self.uuidv4()
        value = self.consul.acl.create_token(
            accessor_id=accessor_id,
            secret_id=secret_id,
            roles=ROLELINKS_SAMPLE,
            policies=POLICYLINKS_SAMPLE,
            service_identities=SERVICE_IDENTITIES_SAMPLE)
        result = self.consul.acl.delete_token(value["AccessorID"])
        self.assertTrue(result)

# -*- coding: utf-8 -*-
"""
These tests require that consul is running on localhost

"""
import functools
import json
try:
    import unittest2 as unittest
except ImportError:
    import unittest
import uuid

import consulate

from consulate.utils import PYTHON3

CONSUL_CONFIG = json.load(open('consul-test.json', 'r'))


def generate_key(func):
    @functools.wraps(func)
    def _decorator(self, *args, **kwargs):
        key = str(uuid.uuid4())[0:8]
        self.used_keys.append(key)
        func(self, key)
    return _decorator


class BaseTestCase(unittest.TestCase):

    def setUp(self):
        self.session = \
            consulate.Consulate(token=CONSUL_CONFIG['acl_master_token'])
        self.used_keys = list()

    def tearDown(self):
        for key in self.used_keys:
            try:
                self.session.kv.delete(key)
            except KeyError:
                pass


class TestACL(BaseTestCase):

    def setUp(self):
        super(TestACL, self).setUp()
        self.acl_list = list()

    def tearDown(self):
        for acl_id in self.acl_list:
            self.session.acl.destroy(acl_id)

    @generate_key
    def test_create_and_destroy(self, key):
        acl_id = self.session.acl.create(key)
        self.acl_list.append(acl_id)
        self.assertTrue(self.session.acl.destroy(acl_id))

    @generate_key
    def test_create_and_info(self, key):
        acl_id = self.session.acl.create(key)
        self.acl_list.append(acl_id)
        self.assertIsNotNone(acl_id)
        data = self.session.acl.info(acl_id)
        self.assertIsNotNone(data)
        self.assertEqual(acl_id, data.get('ID'))

    @generate_key
    def test_create_and_list(self, key):
        acl_id = self.session.acl.create(key)
        self.acl_list.append(acl_id)
        data = self.session.acl.list()
        self.assertIn(acl_id, [r.get('ID') for r in data])

    @generate_key
    def test_create_and_update(self, key):
        acl_id = self.session.acl.create(key)
        self.acl_list.append(acl_id)
        self.session.acl.update(acl_id, 'Foo')
        data = self.session.acl.list()
        self.assertIn('Foo', [r.get('Name') for r in data])
        self.assertIn(acl_id, [r.get('ID') for r in data])


class TestKVGetWithNoKey(BaseTestCase):

    @generate_key
    def test_get_is_none(self, key):
        self.assertIsNone(self.session.kv.get(key))

    @generate_key
    def test_get_item_raises_key_error(self, key):
        self.assertRaises(KeyError, self.session.kv.__getitem__, key)


class TestKVSet(BaseTestCase):

    @generate_key
    def test_set_item_get_item_bool_value(self, key):
        self.session.kv[key] = True
        self.assertTrue(self.session.kv[key])

    @generate_key
    def test_set_item_get_item_int_value(self, key):
        self.session.kv[key] = 128
        self.assertEqual(self.session.kv[key], 128)

    @generate_key
    def test_set_item_get_item_str_value(self, key):
        self.session.kv[key] = b'foo'
        self.assertEqual(self.session.kv[key], 'foo')

    @generate_key
    def test_set_get_bool_value(self, key):
        self.session.kv.set(key, True)
        self.assertTrue(self.session.kv.get(key))

    @generate_key
    def test_set_get_item_value(self, key):
        self.session.kv.set(key, 128)
        self.assertEqual(self.session.kv.get(key), 128)

    @generate_key
    def test_set_item_get_item_str_value(self, key):
        self.session.kv.set(key, b'foo')
        self.assertEqual(self.session.kv.get(key), 'foo')

    @unittest.skipIf(PYTHON3, 'No unicode strings in Python3')
    @generate_key
    def test_set_item_get_item_unicode_value(self, key):
        self.session.kv.set(key, u'✈')
        self.assertEqual(self.session.kv.get(key), u'✈')

    @unittest.skipIf(not PYTHON3, 'No native unicode strings in Python2')
    @generate_key
    def test_set_item_get_item_unicode_value(self, key):
        self.session.kv.set(key, '✈')
        self.assertEqual(self.session.kv.get(key), '✈')

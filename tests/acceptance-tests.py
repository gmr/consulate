# -*- coding: utf-8 -*-
"""
These tests require that consul is running on localhost

"""
import functools
try:
    import unittest2 as unittest
except ImportError:
    import unittest
import uuid

import consulate

from consulate.utils import PYTHON3


def generate_key(func):
    @functools.wraps(func)
    def _decorator(self, *args, **kwargs):
        key = str(uuid.uuid4())
        self.used_keys.append(key)
        func(self, key)
    return _decorator


class BaseTestCase(unittest.TestCase):

    def setUp(self):
        self.session = consulate.Consulate()
        self.used_keys = list()

    def tearDown(self):
        for key in self.used_keys:
            try:
                self.session.kv.delete(key)
            except KeyError:
                pass


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
        print(self.session.kv.get(key))
        self.assertEqual(self.session.kv.get(key), u'✈')

    @unittest.skipIf(not PYTHON3, 'No native unicode strings in Python2')
    @generate_key
    def test_set_item_get_item_unicode_value(self, key):
        self.session.kv.set(key, '✈')
        print(self.session.kv.get(key))
        self.assertEqual(self.session.kv.get(key), '✈')

import json
import unittest
try:
    from urllib import parse  # Python 3
except ImportError:  # pragma: no cover
    import urlparse as parse  # Python 2
import uuid

import httmock

from consulate import adapters, api, utils

from . import base

SCHEME = 'http'
VERSION = 'v1'

ALL_DATA = (b'[{"CreateIndex":643,"ModifyIndex":643,"LockIndex":0,"Key":"bar",'
            b'"Flags":0,"Value":"YmF6"},{"CreateIndex":669,"ModifyIndex":669,"'
            b'LockIndex":0,"Key":"baz","Flags":0,"Value":"cXV4"},{"CreateIndex'
            b'":666,"ModifyIndex":666,"LockIndex":0,"Key":"corgie","Flags":128'
            b',"Value":"ZG9n"},{"CreateIndex":642,"ModifyIndex":642,"LockIndex'
            b'":0,"Key":"foo","Flags":0,"Value":"YmFy"},{"CreateIndex":644,"Mo'
            b'difyIndex":644,"LockIndex":0,"Key":"quz","Flags":0,"Value":"dHJ1'
            b'ZQ=="}]')

ALL_ITEMS = [{
    'CreateIndex': 643,
    'Flags': 0,
    'Key': 'bar',
    'LockIndex': 0,
    'ModifyIndex': 643,
    'Value': 'baz'
}, {
    'CreateIndex': 669,
    'Flags': 0,
    'Key': 'baz',
    'LockIndex': 0,
    'ModifyIndex': 669,
    'Value': 'qux'
}, {
    'CreateIndex': 666,
    'Flags': 128,
    'Key': 'corgie',
    'LockIndex': 0,
    'ModifyIndex': 666,
    'Value': 'dog'
}, {
    'CreateIndex': 642,
    'Flags': 0,
    'Key': 'foo',
    'LockIndex': 0,
    'ModifyIndex': 642,
    'Value': 'bar'
}, {
    'CreateIndex': 644,
    'Flags': 0,
    'Key': 'quz',
    'LockIndex': 0,
    'ModifyIndex': 644,
    'Value': 'true'
}]


@httmock.all_requests
def kv_all_records_content(_url_unused, request):
    return httmock.response(
        200, ALL_DATA, {
            'X-Consul-Index': 4,
            'X-Consul-Knownleader': 'true',
            'X-Consul-Lastcontact': 0,
            'Date': 'Fri, 19 Dec 2014 20:44:28 GMT',
            'Content-Length': len(ALL_DATA),
            'Content-Type': 'application/json'
        }, None, 0, request)


class KVTests(unittest.TestCase):
    def setUp(self):
        self.adapter = adapters.Request()
        self.base_uri = '{0}://localhost:8500/{1}'.format(SCHEME, VERSION)
        self.dc = str(uuid.uuid4())
        self.token = str(uuid.uuid4())
        self.kv = api.KV(self.base_uri, self.adapter, self.dc, self.token)

    def test_contains_evaluates_true(self):
        @httmock.all_requests
        def response_content(_url_unused, request):
            return httmock.response(200, None, {}, None, 0, request)

        with httmock.HTTMock(response_content):
            self.assertIn('foo', self.kv)

    def test_contains_evaluates_false(self):
        @httmock.all_requests
        def response_content(_url_unused, request):
            return httmock.response(404, None, {}, None, 0, request)

        with httmock.HTTMock(response_content):
            self.assertNotIn('foo', self.kv)

    def test_get_all_items(self):
        with httmock.HTTMock(kv_all_records_content):
            for index, row in enumerate(self.kv._get_all_items()):
                self.assertDictEqual(row, ALL_ITEMS[index])

    def test_items(self):
        with httmock.HTTMock(kv_all_records_content):
            for index, row in enumerate(self.kv.items()):
                value = {ALL_ITEMS[index]['Key']: ALL_ITEMS[index]['Value']}
                self.assertDictEqual(row, value)

    def test_iter(self):
        with httmock.HTTMock(kv_all_records_content):
            for index, row in enumerate(self.kv):
                self.assertEqual(row, ALL_ITEMS[index]['Key'])

    def test_iteritems(self):
        with httmock.HTTMock(kv_all_records_content):
            for index, row in enumerate(self.kv.iteritems()):
                value = (ALL_ITEMS[index]['Key'], ALL_ITEMS[index]['Value'])
                self.assertEqual(row, value)

    def test_keys(self):
        expectation = [item['Key'] for item in ALL_ITEMS]
        with httmock.HTTMock(kv_all_records_content):
            self.assertEqual(self.kv.keys(), expectation)

    def test_len(self):
        with httmock.HTTMock(kv_all_records_content):
            self.assertEqual(len(self.kv), len(ALL_ITEMS))

    def test_values(self):
        with httmock.HTTMock(kv_all_records_content):
            for index, row in enumerate(self.kv.values()):
                self.assertEqual(row, ALL_ITEMS[index]['Value'])


class TestKVGetWithNoKey(base.TestCase):
    @base.generate_key
    def test_get_is_none(self, key):
        self.assertIsNone(self.consul.kv.get(key))

    @base.generate_key
    def test_get_item_raises_key_error(self, key):
        self.assertRaises(KeyError, self.consul.kv.__getitem__, key)


class TestKVSet(base.TestCase):
    @base.generate_key
    def test_set_item_del_item(self, key):
        self.consul.kv[key] = 'foo'
        del self.consul.kv[key]
        self.assertNotIn(key, self.consul.kv)

    @base.generate_key
    def test_set_item_get_item_bool_value(self, key):
        self.consul.kv[key] = True
        self.assertTrue(self.consul.kv[key])

    @base.generate_key
    def test_set_path_with_value(self, key):
        path = 'path/{0}/'.format(key)
        self.consul.kv.set(path, 'bar')
        self.assertEqual('bar', self.consul.kv[path[:-1]])

    @base.generate_key
    def test_set_item_get_item_int_value(self, key):
        self.consul.kv[key] = 128
        self.assertEqual(self.consul.kv[key], '128')

    @base.generate_key
    def test_set_item_get_item_str_value(self, key):
        self.consul.kv[key] = b'foo'
        self.assertEqual(self.consul.kv[key], 'foo')

    @base.generate_key
    def test_set_item_get_item_str_value_raw(self, key):
        self.consul.kv[key] = 'foo'
        self.assertEqual(self.consul.kv.get(key, raw=True), 'foo')

    @base.generate_key
    def test_set_get_bool_value(self, key):
        self.consul.kv.set(key, True)
        self.assertTrue(self.consul.kv.get(key))

    @base.generate_key
    def test_set_get_item_value(self, key):
        self.consul.kv.set(key, 128)
        self.assertEqual(self.consul.kv.get(key), '128')

    @base.generate_key
    def test_set_item_get_item_str_value(self, key):
        self.consul.kv.set(key, 'foo')
        self.assertEqual(self.consul.kv.get(key), 'foo')

    @base.generate_key
    def test_set_item_get_record(self, key):
        self.consul.kv.set_record(key, 12, 'record')
        record = self.consul.kv.get_record(key)
        self.assertEqual('record', record['Value'])
        self.assertEqual(12, record['Flags'])
        self.assertIsInstance(record, dict)

    @base.generate_key
    def test_get_record_fail(self, key):
        self.assertEqual(self.consul.kv.get_record(key), None)

    @base.generate_key
    def test_set_record_no_replace_get_item_str_value(self, key):
        self.consul.kv.set(key, 'foo')
        self.consul.kv.set_record(key, 0, 'foo', False)
        self.assertEqual(self.consul.kv.get(key), 'foo')

    @base.generate_key
    def test_set_record_same_value_get_item_str_value(self, key):
        self.consul.kv.set(key, 'foo')
        self.consul.kv.set_record(key, 0, 'foo', True)
        self.assertEqual(self.consul.kv.get(key), 'foo')

    @base.generate_key
    def test_set_item_get_item_dict_value(self, key):
        value = {'foo': 'bar'}
        expectation = json.dumps(value)
        self.consul.kv.set(key, value)
        self.assertEqual(self.consul.kv.get(key), expectation)

    @unittest.skipIf(utils.PYTHON3, 'No unicode strings in Python3')
    @base.generate_key
    def test_set_item_get_item_unicode_value(self, key):
        self.consul.kv.set(key, u'I like to ✈')
        self.assertEqual(self.consul.kv.get(key), u'I like to ✈')

    @unittest.skipIf(not utils.PYTHON3, 'No native unicode strings in Python2')
    @base.generate_key
    def test_set_item_get_item_unicode_value(self, key):
        self.consul.kv.set(key, 'I like to ✈')
        response = self.consul.kv.get(key)
        self.assertEqual(response, 'I like to ✈')

    @base.generate_key
    def test_set_item_in_records(self, key):
        self.consul.kv.set(key, 'zomg')
        expectation = (key, 0, 'zomg')
        self.assertIn(expectation, self.consul.kv.records())

    @base.generate_key
    def test_set_binary_value(self, key):
        value = uuid.uuid4().bytes
        self.consul.kv.set(key, value)
        expectation = (key, 0, value)
        self.assertIn(expectation, self.consul.kv.records())


class TestKVLocking(base.TestCase):
    @base.generate_key
    def test_acquire_and_release_lock(self, key):
        lock_key = str(uuid.uuid4())[0:8]
        session_id = self.consul.session.create(
            key, behavior='delete', ttl='60s')
        self.assertTrue(self.consul.kv.acquire_lock(lock_key, session_id))
        self.assertTrue(self.consul.kv.release_lock(lock_key, session_id))
        self.consul.session.destroy(session_id)

    @base.generate_key
    def test_acquire_and_release_lock(self, key):
        lock_key = str(uuid.uuid4())[0:8]
        sid = self.consul.session.create(key, behavior='delete', ttl='60s')
        sid2 = self.consul.session.create(
            key + '2', behavior='delete', ttl='60s')
        self.assertTrue(self.consul.kv.acquire_lock(lock_key, sid))
        self.assertFalse(self.consul.kv.acquire_lock(lock_key, sid2))
        self.assertTrue(self.consul.kv.release_lock(lock_key, sid))
        self.consul.session.destroy(sid)
        self.consul.session.destroy(sid2)

    @base.generate_key
    def test_acquire_and_release_lock_with_value(self, key):
        lock_key = str(uuid.uuid4())[0:8]
        lock_value = str(uuid.uuid4())
        sid = self.consul.session.create(key, behavior='delete', ttl='60s')
        sid2 = self.consul.session.create(
            key + '2', behavior='delete', ttl='60s')
        self.assertTrue(self.consul.kv.acquire_lock(lock_key, sid, lock_value))
        self.assertEqual(self.consul.kv.get(lock_key), lock_value)
        self.assertFalse(self.consul.kv.acquire_lock(lock_key, sid2))
        self.assertTrue(self.consul.kv.release_lock(lock_key, sid))
        self.consul.session.destroy(sid)
        self.consul.session.destroy(sid2)

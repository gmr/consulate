import httmock
import mock
try:
    import unittest2 as unittest
except ImportError:
    import unittest
try:
    from urllib import parse  # Python 3
except ImportError:  # pragma: no cover
    import urlparse as parse  # Python 2
import uuid

import consulate
from consulate import adapters
from consulate import api

SCHEME = consulate.DEFAULT_SCHEME
VERSION = consulate.VERSION

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
    return httmock.response(200, ALL_DATA, {
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

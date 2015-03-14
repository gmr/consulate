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
        self.consul = consulate.Consul(token=CONSUL_CONFIG['acl_master_token'])
        self.used_keys = list()

    def tearDown(self):
        for key in self.used_keys:
            try:
                self.consul.kv.delete(key)
            except KeyError:
                pass


class TestACL(BaseTestCase):

    def setUp(self):
        super(TestACL, self).setUp()
        self.acl_list = list()

    def tearDown(self):
        for acl_id in self.acl_list:
            self.consul.acl.destroy(acl_id)

    @generate_key
    def test_create_and_destroy(self, key):
        acl_id = self.consul.acl.create(key)
        self.acl_list.append(acl_id)
        self.assertTrue(self.consul.acl.destroy(acl_id))

    @generate_key
    def test_create_and_info(self, key):
        acl_id = self.consul.acl.create(key)
        self.acl_list.append(acl_id)
        self.assertIsNotNone(acl_id)
        data = self.consul.acl.info(acl_id)
        self.assertIsNotNone(data)
        self.assertEqual(acl_id, data.get('ID'))

    @generate_key
    def test_create_and_list(self, key):
        acl_id = self.consul.acl.create(key)
        self.acl_list.append(acl_id)
        data = self.consul.acl.list()
        self.assertIn(acl_id, [r.get('ID') for r in data])

    @generate_key
    def test_create_and_update(self, key):
        acl_id = self.consul.acl.create(key)
        self.acl_list.append(acl_id)
        self.consul.acl.update(acl_id, 'Foo')
        data = self.consul.acl.list()
        self.assertIn('Foo', [r.get('Name') for r in data])
        self.assertIn(acl_id, [r.get('ID') for r in data])


class TestEvent(BaseTestCase):

    def setUp(self):
        super(TestEvent, self).setUp()

    def test_fire(self):
        event_name = 'test-event-%s' % str(uuid.uuid4())[0:8]
        response = self.consul.event.fire(event_name)
        events = self.consul.event.list(event_name)
        if isinstance(events, dict):
            self.assertEqual(event_name, events.get('Name'))
            self.assertEqual(response, events.get('ID'))
        elif isinstance(events, dict):
            self.assertIn(event_name, [e.get('Name') for e in events])
            self.assertIn(response, [e.get('ID') for e in events])
        else:
            assert False, 'Unexpected return type'


class TestKVGetWithNoKey(BaseTestCase):

    @generate_key
    def test_get_is_none(self, key):
        self.assertIsNone(self.consul.kv.get(key))

    @generate_key
    def test_get_item_raises_key_error(self, key):
        self.assertRaises(KeyError, self.consul.kv.__getitem__, key)


class TestKVSet(BaseTestCase):

    @generate_key
    def test_set_item_get_item_bool_value(self, key):
        self.consul.kv[key] = True
        self.assertTrue(self.consul.kv[key])

    @generate_key
    def test_set_item_get_item_int_value(self, key):
        self.consul.kv[key] = 128
        self.assertEqual(self.consul.kv[key], 128)

    @generate_key
    def test_set_item_get_item_str_value(self, key):
        self.consul.kv[key] = b'foo'
        self.assertEqual(self.consul.kv[key], 'foo')

    @generate_key
    def test_set_get_bool_value(self, key):
        self.consul.kv.set(key, True)
        self.assertTrue(self.consul.kv.get(key))

    @generate_key
    def test_set_get_item_value(self, key):
        self.consul.kv.set(key, 128)
        self.assertEqual(self.consul.kv.get(key), 128)

    @generate_key
    def test_set_item_get_item_str_value(self, key):
        self.consul.kv.set(key, b'foo')
        self.assertEqual(self.consul.kv.get(key), 'foo')

    @unittest.skipIf(PYTHON3, 'No unicode strings in Python3')
    @generate_key
    def test_set_item_get_item_unicode_value(self, key):
        self.consul.kv.set(key, u'✈')
        self.assertEqual(self.consul.kv.get(key), u'✈')

    @unittest.skipIf(not PYTHON3, 'No native unicode strings in Python2')
    @generate_key
    def test_set_item_get_item_unicode_value(self, key):
        self.consul.kv.set(key, '✈')
        self.assertEqual(self.consul.kv.get(key), '✈')


class TestSession(unittest.TestCase):

    def setUp(self):
        self.consul = consulate.Consul(token=CONSUL_CONFIG['acl_master_token'])
        self.sessions = list()

    def tearDown(self):
        for session in self.sessions:
            self.consul.session.destroy(session)

    def test_session_create(self):
        name = str(uuid.uuid4())[0:8]
        session_id = self.consul.session.create(name, behavior='delete',
                                                ttl='60s')
        self.sessions.append(session_id)
        self.assertIsNotNone(session_id)

    def test_session_destroy(self):
        name = str(uuid.uuid4())[0:8]
        session_id = self.consul.session.create(name, behavior='delete',
                                                ttl='60s')
        self.consul.session.destroy(session_id)
        self.assertNotIn(session_id, [s.get('ID') for s in
                                      self.consul.session.list()])

    def test_session_info(self):
        name = str(uuid.uuid4())[0:8]
        session_id = self.consul.session.create(name, behavior='delete',
                                                ttl='60s')
        result = self.consul.session.info(session_id)
        self.assertEqual(session_id, result.get('ID'))
        self.consul.session.destroy(session_id)

    def test_session_renew(self):
        name = str(uuid.uuid4())[0:8]
        session_id = self.consul.session.create(name, behavior='delete',
                                                ttl='60s')
        self.sessions.append(session_id)
        self.assertTrue(self.consul.session.renew(session_id))


class TestKVLocking(BaseTestCase):

    @generate_key
    def test_acquire_and_release_lock(self, key):
        lock_key = str(uuid.uuid4())[0:8]
        session_id = self.consul.session.create(key, behavior='delete',
                                                ttl='60s')
        self.assertTrue(self.consul.kv.acquire_lock(lock_key, session_id))
        self.assertTrue(self.consul.kv.release_lock(lock_key, session_id))
        self.consul.session.destroy(session_id)

    @generate_key
    def test_acquire_and_release_lock(self, key):
        lock_key = str(uuid.uuid4())[0:8]
        sid = self.consul.session.create(key, behavior='delete', ttl='60s')
        sid2 = self.consul.session.create(key + '2', behavior='delete',
                                          ttl='60s')
        self.assertTrue(self.consul.kv.acquire_lock(lock_key, sid))
        self.assertFalse(self.consul.kv.acquire_lock(lock_key, sid2))
        self.assertTrue(self.consul.kv.release_lock(lock_key, sid))
        self.consul.session.destroy(sid)
        self.consul.session.destroy(sid2)

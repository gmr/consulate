"""
Tests for Consulate.agent

"""
import uuid

import consulate

from . import base


class TestCase(base.TestCase):
    def test_checks(self):
        result = self.consul.agent.checks()
        self.assertDictEqual(result, {})

    def test_force_leave(self):
        self.assertTrue(self.consul.agent.force_leave(str(uuid.uuid4())))

    def test_force_leave_forbidden(self):
        with self.assertRaises(consulate.Forbidden):
            self.forbidden_consul.agent.force_leave(str(uuid.uuid4()))

    def test_join(self):
        self.assertTrue(self.consul.agent.join('127.0.0.1'))

    def test_join_forbidden(self):
        with self.assertRaises(consulate.Forbidden):
            self.forbidden_consul.agent.join('255.255.255.255')

    def test_maintenance(self):
        self.consul.agent.maintenance(True, 'testing')
        self.consul.agent.maintenance(False)

    def test_maintenance_forbidden(self):
        with self.assertRaises(consulate.Forbidden):
            self.forbidden_consul.agent.maintenance(True)

    def test_members(self):
        result = self.consul.agent.members()
        self.assertEqual(len(result), 1)

    def test_members_forbidden(self):
        with self.assertRaises(consulate.Forbidden):
            self.forbidden_consul.agent.members()

    def test_metrics(self):
        result = self.consul.agent.metrics()
        self.assertIn('Timestamp', result)
        self.assertIn('Gauges', result)

    def test_metrics_forbidden(self):
        with self.assertRaises(consulate.Forbidden):
            self.forbidden_consul.agent.metrics()

    def test_monitor(self):
        for line in self.consul.agent.monitor():
            self.assertIsInstance(line, str)
            break

    def test_monitor_forbidden(self):
        with self.assertRaises(consulate.Forbidden):
            for line in self.forbidden_consul.agent.monitor():
                self.assertIsInstance(line, str)
                break

    def test_reload(self):
        self.assertIsNone(self.consul.agent.reload())

    def test_reload_forbidden(self):
        with self.assertRaises(consulate.Forbidden):
            self.forbidden_consul.agent.reload()

    def test_self(self):
        result = self.consul.agent.self()
        self.assertIn('Config', result)
        self.assertIn('Coord', result)
        self.assertIn('Member', result)

    def test_self_forbidden(self):
        with self.assertRaises(consulate.Forbidden):
            self.forbidden_consul.agent.self()

    def test_service_registration(self):
        self.consul.agent.service.register(
            'test-service', address='10.0.0.1', port=5672, tags=['foo', 'bar'])
        self.assertIn('test-service', self.consul.agent.services())
        self.consul.agent.service.deregister('test-service')

    def test_token(self):
        self.assertTrue(
            self.consul.agent.token('acl_replication_token', 'foo'))

    def test_token_invalid(self):
        with self.assertRaises(ValueError):
            self.consul.agent.token('acl_replication_tokens', 'foo')

    def test_token_forbidden(self):
        with self.assertRaises(consulate.Forbidden):
            self.forbidden_consul.agent.token('acl_replication_token', 'foo')


class CheckTestCase(base.TestCase):

    def test_register(self):
        self.assertTrue(self.consul.agent.check.register(
            str(uuid.uuid4()), http='http://localhost', interval=30))

    def test_register_script_and_no_interval(self):
        with self.assertRaises(ValueError):
            self.forbidden_consul.agent.check.register(
                str(uuid.uuid4()),  '/bin/true')

    def test_register_script_and_ttl(self):
        with self.assertRaises(ValueError):
            self.forbidden_consul.agent.check.register(
                str(uuid.uuid4()), script='/bin/true', ttl=30)

    def test_register_http_and_no_interval(self):
        with self.assertRaises(ValueError):
            self.forbidden_consul.agent.check.register(
                str(uuid.uuid4()), http='http://localhost')

    def test_register_script_and_http(self):
        with self.assertRaises(ValueError):
            self.forbidden_consul.agent.check.register(
                str(uuid.uuid4()), script='/bin/true', http='http://localhost')

    def test_register_forbidden(self):
        with self.assertRaises(consulate.Forbidden):
            self.forbidden_consul.agent.check.register(
                str(uuid.uuid4()), '/bin/true', interval=30)


class TTLCheckTestCase(base.TestCase):

    def setUp(self):
        super(TTLCheckTestCase, self).setUp()
        name = str(uuid.uuid4())
        self.assertTrue(self.consul.agent.check.register(name, ttl=30))
        checks = self.consul.agent.checks()
        self.check_id = checks[name]['CheckID']

    def test_pass(self):
        self.assertTrue(self.consul.agent.check.ttl_pass(self.check_id))

    def test_pass_with_note(self):
        self.assertTrue(
            self.consul.agent.check.ttl_pass(self.check_id, 'PASS'))

    def test_warn(self):
        self.assertTrue(self.consul.agent.check.ttl_warn(self.check_id))

    def test_warn_with_note(self):
        self.assertTrue(
            self.consul.agent.check.ttl_warn(self.check_id, 'WARN'))

    def test_fail(self):
        self.assertTrue(self.consul.agent.check.ttl_fail(self.check_id))

    def test_fail_with_note(self):
        self.assertTrue(
            self.consul.agent.check.ttl_fail(self.check_id, 'FAIL'))


class ServiceTestCase(base.TestCase):

    def test_register(self):
        self.assertTrue(self.consul.agent.service.register(
            str(uuid.uuid4()),
            address='127.0.0.1',
            port=80,
            script='/bin/true',
            interval=30,
            tags=[str(uuid.uuid4())]))

    def test_register_http(self):
        self.assertTrue(self.consul.agent.service.register(
            str(uuid.uuid4()),
            address='127.0.0.1',
            port=80,
            http='http://localhost',
            interval=30,
            tags=[str(uuid.uuid4())]))

    def test_register_ttl(self):
        self.assertTrue(self.consul.agent.service.register(
            str(uuid.uuid4()),
            address='127.0.0.1',
            port=80,
            ttl=30,
            tags=[str(uuid.uuid4())]))

    def test_register_forbidden(self):
        with self.assertRaises(consulate.Forbidden):
            self.forbidden_consul.agent.service.register(
                str(uuid.uuid4()),
                address='127.0.0.1',
                port=80,
                tags=[str(uuid.uuid4())])

    def test_register_invalid_port(self):
        with self.assertRaises(ValueError):
            self.consul.agent.service.register(
                str(uuid.uuid4()),
                address='127.0.0.1',
                port='80',
                ttl=30,
                tags=[str(uuid.uuid4())])

    def test_register_invalid_tags(self):
        with self.assertRaises(ValueError):
            self.consul.agent.service.register(
                str(uuid.uuid4()),
                address='127.0.0.1',
                ttl=30,
                tags=str(uuid.uuid4()))

    def test_register_invalid_interval(self):
        with self.assertRaises(ValueError):
            self.consul.agent.service.register(
                str(uuid.uuid4()),
                address='127.0.0.1',
                port=80,
                http='http://localhost',
                interval='30',
                tags=[str(uuid.uuid4())])

    def test_register_invalid_ttl(self):
        with self.assertRaises(ValueError):
            self.consul.agent.service.register(
                str(uuid.uuid4()),
                address='127.0.0.1',
                port=80,
                ttl=-30,
                tags=[str(uuid.uuid4())])

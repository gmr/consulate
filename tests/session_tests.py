import uuid

from . import base


class TestSession(base.TestCase):
    def setUp(self):
        super(TestSession, self).setUp()
        self.sessions = list()

    def tearDown(self):
        for session in self.sessions:
            self.consul.session.destroy(session)

    def test_session_create(self):
        name = str(uuid.uuid4())[0:8]
        session_id = self.consul.session.create(
            name, behavior='delete', ttl='60s')
        self.sessions.append(session_id)
        self.assertIsNotNone(session_id)

    def test_session_destroy(self):
        name = str(uuid.uuid4())[0:8]
        session_id = self.consul.session.create(
            name, behavior='delete', ttl='60s')
        self.consul.session.destroy(session_id)
        self.assertNotIn(session_id,
                         [s.get('ID') for s in self.consul.session.list()])

    def test_session_info(self):
        name = str(uuid.uuid4())[0:8]
        session_id = self.consul.session.create(
            name, behavior='delete', ttl='60s')
        result = self.consul.session.info(session_id)
        self.assertEqual(session_id, result.get('ID'))
        self.consul.session.destroy(session_id)

    def test_session_renew(self):
        name = str(uuid.uuid4())[0:8]
        session_id = self.consul.session.create(
            name, behavior='delete', ttl='60s')
        self.sessions.append(session_id)
        self.assertTrue(self.consul.session.renew(session_id))

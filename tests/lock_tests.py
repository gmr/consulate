import uuid

from . import base


class TestLock(base.TestCase):
    def test_lock_as_context_manager(self):
        value = str(uuid.uuid4())
        with self.consul.lock.acquire(value=value):
            self.assertEqual(self.consul.kv.get(self.consul.lock.key), value)

import uuid

from . import base


class TestEvent(base.TestCase):
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

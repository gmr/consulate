from . import base

class TestCoordinate(base.TestCase):
    def test_coordinate(self):
        coordinates = self.consul.coordinate.nodes()
        self.assertIsInstance(coordinates, list)

from . import base


class TestCatalog(base.TestCase):
    def test_catalog_registration(self):
        self.consul.catalog.register('test-service', address='10.0.0.1')
        self.assertIn('test-service',
                      [n['Node'] for n in self.consul.catalog.nodes()])
        self.consul.catalog.deregister('test-service')
        self.assertNotIn('test-service',
                         [n['Node'] for n in self.consul.catalog.nodes()])

import json
import httmock
import mock
try:
    import unittest2 as unittest
except ImportError:
    import unittest
try:
    from urllib import parse  # Python 3
except ImportError:  # pragma: no cover
    import urlparse as parse      # Python 2
import uuid

import consulate
from consulate import adapters
from consulate.api import base

CONSUL_CONFIG = json.load(open('consul-test.json', 'r'))

SCHEME = consulate.DEFAULT_SCHEME
VERSION = consulate.VERSION


class ConsulTests(unittest.TestCase):

    @mock.patch('consulate.adapters.Request')
    @mock.patch('consulate.api.Agent')
    @mock.patch('consulate.api.Catalog')
    @mock.patch('consulate.api.KV')
    @mock.patch('consulate.api.Health')
    @mock.patch('consulate.api.ACL')
    @mock.patch('consulate.api.Event')
    @mock.patch('consulate.api.Session')
    @mock.patch('consulate.api.Status')
    def setUp(self, status, session, event, acl, health, kv, catalog,
              agent, adapter):
        self.host = '127.0.0.1'
        self.port = 8500
        self.dc = CONSUL_CONFIG['datacenter']
        self.token = CONSUL_CONFIG['acl_master_token']

        self.acl = acl
        self.adapter = adapter
        self.agent = agent
        self.catalog = catalog
        self.event = event
        self.kv = kv
        self.health = health
        self.session = session
        self.status = status

        self.base_uri = '{0}://{1}:{2}/v1'.format(SCHEME,
                                                  self.host, self.port)
        self.consul = consulate.Consul(self.host, self.port, self.dc,
                                       self.token)

    def test_base_uri(self):
        self.assertEquals(self.consul._base_uri(SCHEME, self.host, self.port),
                          self.base_uri)

    def test_unix_socket_base_uri(self):
        expectation = 'http+unix://%2Fvar%2Flib%2Fconsul%2Fconsul.sock/v1'
        self.assertEquals(self.consul._base_uri('http+unix',
                                                '/var/lib/consul/consul.sock',
                                                None),
                          expectation)

    def test_acl_initialization(self):
        self.assertTrue(self.acl.called_once_with(self.base_uri,
                                                  self.adapter, self.dc,
                                                  self.token))

    def test_adapter_initialization(self):
        self.assertTrue(self.adapter.called_once_with())

    def test_agent_initialization(self):
        self.assertTrue(self.agent.called_once_with(self.base_uri,
                                                    self.adapter,
                                                    self.dc, self.token))

    def test_catalog_initialization(self):
        self.assertTrue(self.catalog.called_once_with(self.base_uri,
                                                      self.adapter, self.dc,
                                                      self.token))

    def test_events_initialization(self):
        self.assertTrue(self.event.called_once_with(self.base_uri,
                                                    self.adapter, self.dc,
                                                    self.token))

    def test_kv_initialization(self):
        self.assertTrue(self.kv.called_once_with(self.base_uri, self.adapter,
                                                 self.dc, self.token))

    def test_health_initialization(self):
        self.assertTrue(self.health.called_once_with(self.base_uri,
                                                     self.adapter, self.dc,
                                                     self.token))

    def test_session_initialization(self):
        self.assertTrue(self.session.called_once_with(self.base_uri,
                                                      self.adapter, self.dc,
                                                      self.token))

    def test_status_initialization(self):
        self.assertTrue(self.status.called_once_with(self.base_uri,
                                                     self.adapter, self.dc,
                                                     self.token))

    def test_acl_property(self):
        self.assertEqual(self.consul.acl, self.consul._acl)

    def test_agent_property(self):
        self.assertEqual(self.consul.agent, self.consul._agent)

    def test_catalog_property(self):
        self.assertEqual(self.consul.catalog, self.consul._catalog)

    def test_event_property(self):
        self.assertEqual(self.consul.event, self.consul._event)

    def test_health_property(self):
        self.assertEqual(self.consul.health, self.consul._health)

    def test_kv_property(self):
        self.assertEqual(self.consul.kv, self.consul._kv)

    def test_status_property(self):
        self.assertEqual(self.consul.status, self.consul._status)


class EndpointBuildURITests(unittest.TestCase):

    def setUp(self):
        self.adapter = adapters.Request()
        self.base_uri = '{0}://localhost:8500/{1}'.format(SCHEME, VERSION)
        self.endpoint = base.Endpoint(self.base_uri, self.adapter)

    def test_adapter_assignment(self):
        self.assertEqual(self.endpoint._adapter, self.adapter)

    def test_base_uri_assignment(self):
        self.assertEqual(self.endpoint._base_uri,
                         '{0}/endpoint'.format(self.base_uri))

    def test_dc_assignment(self):
        self.assertIsNone(self.endpoint._dc)

    def test_token_assignment(self):
        self.assertIsNone(self.endpoint._token)

    def test_build_uri_with_no_params(self):
        result = self.endpoint._build_uri(['foo', 'bar'])
        parsed = parse.urlparse(result)
        query_params = parse.parse_qs(parsed.query)
        self.assertEqual(parsed.scheme, SCHEME)
        self.assertEqual(parsed.netloc, 'localhost:8500')
        self.assertEqual(parsed.path, '/{0}/endpoint/foo/bar'.format(VERSION))
        self.assertDictEqual(query_params, {})

    def test_build_uri_with_params(self):
        result = self.endpoint._build_uri(['foo', 'bar'], {'baz': 'qux'})
        parsed = parse.urlparse(result)
        query_params = parse.parse_qs(parsed.query)
        self.assertEqual(parsed.scheme, SCHEME)
        self.assertEqual(parsed.netloc, 'localhost:8500')
        self.assertEqual(parsed.path, '/{0}/endpoint/foo/bar'.format(VERSION))
        self.assertDictEqual(query_params, {'baz': ['qux']})


class EndpointBuildURIWithDCTests(unittest.TestCase):

    def setUp(self):
        self.adapter = adapters.Request()
        self.base_uri = '{0}://localhost:8500/{1}'.format(SCHEME, VERSION)
        self.dc = str(uuid.uuid4())
        self.endpoint = base.Endpoint(self.base_uri, self.adapter, self.dc)

    def test_dc_assignment(self):
        self.assertEqual(self.endpoint._dc, self.dc)

    def test_token_assignment(self):
        self.assertIsNone(self.endpoint._token)

    def test_build_uri_with_no_params(self):
        result = self.endpoint._build_uri(['foo', 'bar'])
        parsed = parse.urlparse(result)
        query_params = parse.parse_qs(parsed.query)
        self.assertEqual(parsed.scheme, SCHEME)
        self.assertEqual(parsed.netloc, 'localhost:8500')
        self.assertEqual(parsed.path, '/{0}/endpoint/foo/bar'.format(VERSION))
        self.assertDictEqual(query_params, {'dc': [self.dc]})

    def test_build_uri_with_params(self):
        result = self.endpoint._build_uri(['foo', 'bar'], {'baz': 'qux'})
        parsed = parse.urlparse(result)
        query_params = parse.parse_qs(parsed.query)
        self.assertEqual(parsed.scheme, SCHEME)
        self.assertEqual(parsed.netloc, 'localhost:8500')
        self.assertEqual(parsed.path, '/{0}/endpoint/foo/bar'.format(VERSION))
        self.assertDictEqual(query_params, {'dc': [self.dc],
                                            'baz': ['qux']})


class EndpointBuildURIWithTokenTests(unittest.TestCase):

    def setUp(self):
        self.adapter = adapters.Request()
        self.base_uri = '{0}://localhost:8500/{1}'.format(SCHEME, VERSION)
        self.token = str(uuid.uuid4())
        self.endpoint = base.Endpoint(self.base_uri, self.adapter,
                                      token=self.token)

    def test_dc_assignment(self):
        self.assertIsNone(self.endpoint._dc)

    def test_token_assignment(self):
        self.assertEqual(self.endpoint._token, self.token)

    def test_build_uri_with_no_params(self):
        result = self.endpoint._build_uri(['foo', 'bar'])
        parsed = parse.urlparse(result)
        query_params = parse.parse_qs(parsed.query)
        self.assertEqual(parsed.scheme, SCHEME)
        self.assertEqual(parsed.netloc, 'localhost:8500')
        self.assertEqual(parsed.path, '/{0}/endpoint/foo/bar'.format(VERSION))
        self.assertDictEqual(query_params, {'token': [self.token]})

    def test_build_uri_with_params(self):
        result = self.endpoint._build_uri(['foo', 'bar'], {'baz': 'qux'})
        parsed = parse.urlparse(result)
        query_params = parse.parse_qs(parsed.query)
        self.assertEqual(parsed.scheme, SCHEME)
        self.assertEqual(parsed.netloc, 'localhost:8500')
        self.assertEqual(parsed.path, '/{0}/endpoint/foo/bar'.format(VERSION))
        self.assertDictEqual(query_params, {'token': [self.token],
                                            'baz': ['qux']})


class EndpointBuildURIWithDCAndTokenTests(unittest.TestCase):

    def setUp(self):
        self.adapter = adapters.Request()
        self.base_uri = '{0}://localhost:8500/{1}'.format(SCHEME, VERSION)
        self.dc = str(uuid.uuid4())
        self.token = str(uuid.uuid4())
        self.endpoint = base.Endpoint(self.base_uri, self.adapter, self.dc,
                                      self.token)

    def test_dc_assignment(self):
        self.assertEqual(self.endpoint._dc, self.dc)

    def test_token_assignment(self):
        self.assertEqual(self.endpoint._token, self.token)

    def test_build_uri_with_no_params(self):
        result = self.endpoint._build_uri(['foo', 'bar'])
        parsed = parse.urlparse(result)
        query_params = parse.parse_qs(parsed.query)
        self.assertEqual(parsed.scheme, SCHEME)
        self.assertEqual(parsed.netloc, 'localhost:8500')
        self.assertEqual(parsed.path, '/{0}/endpoint/foo/bar'.format(VERSION))
        self.assertDictEqual(query_params, {'dc': [self.dc],
                                            'token': [self.token]})

    def test_build_uri_with_params(self):
        result = self.endpoint._build_uri(['foo', 'bar'], {'baz': 'qux'})
        parsed = parse.urlparse(result)
        query_params = parse.parse_qs(parsed.query)
        self.assertEqual(parsed.scheme, SCHEME)
        self.assertEqual(parsed.netloc, 'localhost:8500')
        self.assertEqual(parsed.path, '/{0}/endpoint/foo/bar'.format(VERSION))
        self.assertDictEqual(query_params, {'dc': [self.dc],
                                            'token': [self.token],
                                            'baz': ['qux']})


class EndpointGetTests(unittest.TestCase):

    def setUp(self):
        self.adapter = adapters.Request()
        self.base_uri = '{0}://localhost:8500/{1}'.format(SCHEME, VERSION)
        self.dc = str(uuid.uuid4())
        self.token = str(uuid.uuid4())
        self.endpoint = base.Endpoint(self.base_uri, self.adapter, self.dc,
                                      self.token)

    def test_get_200_returns_response_body(self):
        @httmock.all_requests
        def response_content(_url_unused, request):
            headers = {'X-Consul-Index': 4,
                       'X-Consul-Knownleader': 'true',
                       'X-Consul-Lastcontact': 0,
                       'Date': 'Fri, 19 Dec 2014 20:44:28 GMT',
                       'Content-Length': 13,
                       'Content-Type': 'application/json'}
            content = b'{"consul": []}'
            return httmock.response(200, content, headers, None, 0, request)

        with httmock.HTTMock(response_content):
            values = self.endpoint._get([str(uuid.uuid4())])
            self.assertEqual(values, {'consul': []})

    def test_get_404_returns_empty_list(self):
        @httmock.all_requests
        def response_content(_url_unused, request):
            headers = {'content-length': 0,
                       'content-type': 'text/plain; charset=utf-8'}
            return httmock.response(404, None, headers, None, 0, request)

        with httmock.HTTMock(response_content):
            values = self.endpoint._get([str(uuid.uuid4())])
            self.assertEqual(values, [])


class EndpointGetListTests(unittest.TestCase):

    def setUp(self):
        self.adapter = adapters.Request()
        self.base_uri = '{0}://localhost:8500/{1}'.format(SCHEME, VERSION)
        self.dc = str(uuid.uuid4())
        self.token = str(uuid.uuid4())
        self.endpoint = base.Endpoint(self.base_uri, self.adapter, self.dc,
                                      self.token)

    def test_get_list_200_returns_response_body(self):
        @httmock.all_requests
        def response_content(_url_unused, request):
            headers = {'X-Consul-Index': 4,
                       'X-Consul-Knownleader': 'true',
                       'X-Consul-Lastcontact': 0,
                       'Date': 'Fri, 19 Dec 2014 20:44:28 GMT',
                       'Content-Length': 13,
                       'Content-Type': 'application/json'}
            content = b'{"consul": []}'
            return httmock.response(200, content, headers, None, 0, request)

        with httmock.HTTMock(response_content):
            values = self.endpoint._get_list([str(uuid.uuid4())])
            self.assertEqual(values, [{'consul': []}])

    def test_get_list_404_returns_empty_list(self):
        @httmock.all_requests
        def response_content(_url_unused, request):
            headers = {'content-length': 0,
                       'content-type': 'text/plain; charset=utf-8'}
            return httmock.response(404, None, headers, None, 0, request)

        with httmock.HTTMock(response_content):
            values = self.endpoint._get_list([str(uuid.uuid4())])
            self.assertEqual(values, [])

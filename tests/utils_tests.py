# coding=utf-8
import unittest

from consulate import exceptions, utils


class QuoteTestCase(unittest.TestCase):
    def urlencode_test(self):
        self.assertEqual("%2Ffoo%40bar", utils.quote("/foo@bar", ""))


class MaybeEncodeTestCase(unittest.TestCase):
    @unittest.skipUnless(utils.PYTHON3, 'Python3 Only')
    def str_test(self):
        self.assertEqual(utils.maybe_encode('foo'), b'foo')

    @unittest.skipUnless(utils.PYTHON3, 'Python3 Only')
    def byte_test(self):
        self.assertEqual(utils.maybe_encode(b'bar'), b'bar')


class Response(object):
    def __init__(self, status_code=200, body=b'content'):
        self.status_code = status_code
        self.body = body


class ResponseOkTestCase(unittest.TestCase):

    def test_200(self):
        self.assertTrue(utils.response_ok(Response(200, b'ok')))

    def test_400(self):
        with self.assertRaises(exceptions.ClientError):
            utils.response_ok(Response(400, b'Bad request'))

    def test_401(self):
        with self.assertRaises(exceptions.ACLDisabled):
            utils.response_ok(Response(401, b'What ACL?'))

    def test_403(self):
        with self.assertRaises(exceptions.Forbidden):
            utils.response_ok(Response(403, b'No'))

    def test_404_not_raising(self):
        self.assertFalse(utils.response_ok(Response(404, b'not found')))

    def test_404_raising(self):
        with self.assertRaises(exceptions.NotFound):
            utils.response_ok(Response(404, b'Not Found'), True)

    def test_500(self):
        with self.assertRaises(exceptions.ServerError):
            utils.response_ok(Response(500, b'Opps'))




class ValidateGoDurationTestCase(unittest.TestCase):

    def test_valid_values(self):
        for value in {'5µs', '300ms', '-1.5h', '2h45m', '5m', '30s'}:
            print('Testing {}'.format(value))
            self.assertTrue(utils.validate_go_interval(value))

    def test_invalid_values(self):
        for value in {'100', '1 year', '5M', '30S'}:
            print('Testing {}'.format(value))
            self.assertFalse(utils.validate_go_interval(value))


class ValidateURLTestCase(unittest.TestCase):

    def test_valid_values(self):
        for value in {'https://foo', 'http://localhost/bar'}:
            print('Testing {}'.format(value))
            self.assertTrue(utils.validate_url(value))

    def test_invalid_values(self):
        for value in {'localhost', 'a'}:
            print('Testing {}'.format(value))
            self.assertFalse(utils.validate_url(value))



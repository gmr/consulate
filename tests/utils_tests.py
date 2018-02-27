# coding=utf-8
import unittest

from consulate import utils


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


class ValidateGoDurationTestCase(unittest.TestCase):

    def test_valid_values(self):
        for value in {'5µs', '300ms', '-1.5h', '2h45m', '5m', '30s'}:
            print('Testing {}'.format(value))
            self.assertTrue(utils.validate_go_interval(value))

    def test_invalid_values(self):
        for value in {'100', '1 year', '5M', '30S'}:
            print('Testing {}'.format(value))
            self.assertFalse(utils.validate_go_interval(value))

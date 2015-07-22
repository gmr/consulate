try:
    import unittest2 as unittest
except ImportError:
    import unittest

from consulate import utils


class TestQuote(unittest.TestCase):

    def urlencode_test(self):
        self.assertEqual("%2Ffoo%40bar", utils.quote("/foo@bar", ""))


class TestMaybeEncode(unittest.TestCase):

    @unittest.skipUnless(utils.PYTHON3, 'Python3 Only')
    def str_test(self):
        self.assertEqual(utils.maybe_encode('foo'), b'foo')

    @unittest.skipUnless(utils.PYTHON3, 'Python3 Only')
    def byte_test(self):
        self.assertEqual(utils.maybe_encode(b'bar'), b'bar')

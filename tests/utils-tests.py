try:
    import unittest2 as unittest
except ImportError:
    import unittest

from consulate import utils


class TestQuote(unittest.TestCase):

    def urlencode_test(self):
        self.assertEqual("%2Ffoo%40bar", utils.quote("/foo@bar", ""))

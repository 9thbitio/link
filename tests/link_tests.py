import unittest
from vlinks import DebugLink, MockWrapper, MockLink

debug = DebugLink()

class TestLink(unittest.TestCase):

    def setUp(self):
        self.mock = MockLink()

    def test_global_file(self):
        self.assertTrue(True)

    def test_false(self):
        self.assertTrue(True)

if __name__ == '__main__':
        unittest.main()

import unittest
from vlinks import DebugLink, Linker
from vlinks.link import MockLink, MockWrapper

debug = DebugLink()

class MockDebugLink(MockLink):

    def __init__(self):
        super(MockLink, self).__init__('', MockDebugWrapper)

    def mock_func(self, name, blah = False):
        return "listened"

class MockDebugWrapper(MockWrapper):

    def mock_func(self, name, blah = False):
        return "listened"



class TestLink(unittest.TestCase):

    def setUp(self):
        self.mocklink = MockDebugLink()
        self.mockwrapper = self.mocklink()

    def test_debug_inspect_wrapper(self):
        listen_out = self.mockwrapper.debug_inspect('mock_func', 'input', blah=True)
        self.assertEquals(listen_out['result'], 'listened')
        self.assertEquals(listen_out['function'].__name__, 'debug_inspect' )
        self.assertEquals(listen_out['kargs'][2], 'input')
        self.assertEquals(listen_out['kwargs'], {'blah':True})

    def test_debug_listen_wrapper(self):
        listen_out = self.mockwrapper.debug_listen('mock_func', 'input', blah=True)
        self.assertEquals(listen_out['function'].__name__, 'debug_listen' )
        self.assertEquals(listen_out['kargs'][2], 'input')
        self.assertFalse(listen_out.has_key('blah'))

    def test_debug_inspect_link(self):
        listen_out = self.mocklink.debug_inspect('mock_func', 'input', blah=True)
        self.assertEquals(listen_out['result'], 'listened')
        self.assertEquals(listen_out['function'].__name__, 'debug_inspect')
        self.assertEquals(listen_out['kargs'][2], 'input')
        self.assertEquals(listen_out['kwargs'], {'blah':True})

    def test_debug_listen_link(self):
        listen_out = self.mocklink.debug_listen('mock_func', 'input', blah=True)
        self.assertEquals(listen_out['function'].__name__, 'debug_listen')
        self.assertEquals(listen_out['kargs'][2], 'input')
        self.assertFalse(listen_out.has_key('blah'))



if __name__ == '__main__':
        unittest.main()

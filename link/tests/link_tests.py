import unittest
from link import Link, Linker
from link.utils import load_json_file
from mock import Mock

#have to be careful that we have not called instance before
lnk = Link.instance(config_file='test_link.config')

class TestLink(unittest.TestCase):

    def setUp(self):
        self.link = lnk

    def test_config(self):
        self.assertEquals(self.link.config, load_json_file('test_link.config'))

    def test_instance(self):
        self.assertNotEquals(self.link, Link('test_link.config'))
        #check to make sure this is a singleton
        self.assertEquals(self.link,
                          Link.instance(config_file='test_link.config'))

class TestLinker(unittest.TestCase):

    def setUp(self):
        self.linker = Linker('dbs')  

    def test_config(self):
        

class TestWrapper(unittest.TestCase):
    pass

if __name__ == '__main__':
    import nose
    nose.runmodule(argv=[__file__,'-vvs','-x','--pdb', '--pdb-failure'],
                   exit=False)
        


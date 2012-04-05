import unittest
import os
from link import Link
from link.utils import load_json_file
from mock import Mock

TEST_CONFIG = '%s/test_link.config' % (os.path.dirname(__file__))

#have to be careful that we have not called instance before
lnk = Link.instance(config_file=TEST_CONFIG)

class TestLink(unittest.TestCase):

    def setUp(self):
        self.link = lnk

    def test_config(self):
        self.assertEquals(self.link.config, load_json_file(TEST_CONFIG))

    def test_instance(self):
        self.assertNotEquals(self.link, Link(TEST_CONFIG))
        #check to make sure this is a singleton
        self.assertEquals(self.link,
                          Link.instance(config_file=TEST_CONFIG))

    def test_config_lookup(self):
        lookup = self.link.config('apis.test_api')
        print lookup


class TestWrapper(unittest.TestCase):
    pass

if __name__ == '__main__':
    import nose
    nose.runmodule(argv=[__file__,'-vvs','-x','--pdb', '--pdb-failure'],
                   exit=False)
        


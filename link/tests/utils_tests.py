from link.utils import *
from link.tests import *
import unittest


class TestUtils(unittest.TestCase):

    def setUp(self):
        pass

    def test_no_such_file(self):
        self.assertRaises(Exception, load_json_file, 'this is not a file')

    def test_bad_json(self):
        bad_config = tst_config_path('bad_json.config')
        self.assertRaises(Exception, load_json_file, bad_config)

if __name__ == '__main__':
    import nose
    nose.runmodule(argv=[__file__,'-vvs','-x','--pdb', '--pdb-failure'],
                   exit=False)
        

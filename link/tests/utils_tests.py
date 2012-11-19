from link.utils import *
from link.tests import *
import unittest


class TestUtils(unittest.TestCase):

    def setUp(self):
        pass

    def test_no_such_file(self):
        self.assertRaises(Exception, load_json_file, 'this is not a file')

    def test_bad_json(self):
        bad_config = tst_config_path('bad_json.test_config')
        self.assertRaises(Exception, load_json_file, bad_config)

    def test_pagenate(self):
        data = [1,2,3,4,5]
        data = [x for x in array_pagenate(4,data, padvalue = 5)]
        self.assertEquals(data, [(1,2,3,4), (5,5,5,5)])

if __name__ == '__main__':
    import nose
    nose.runmodule(argv=[__file__,'-vvs','-x','--pdb', '--pdb-failure'],
                   exit=False)
        

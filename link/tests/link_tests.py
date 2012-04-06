import unittest
import os
from link import Link
from link.utils import load_json_file
from link.tests import *

DIR = os.path.dirname(__file__)
TEST_CONFIG = 'test_link.test_config' 
TEST_CONFIG2 = 'test_link2.test_config'

#load in all the configs that we want
lnk = Link.instance()
config1 = load_tst_config(TEST_CONFIG)
config1_path = tst_config_path(TEST_CONFIG)
config2 = load_tst_config(TEST_CONFIG2)
config2_path = tst_config_path(TEST_CONFIG2)

class TestLink(unittest.TestCase):

    def setUp(self):
        #reset the config every time to config1
        lnk.fresh(config_file=config1_path)

    def test_config(self):
        self.assertEquals(lnk.config(), config1)

    def test_instance(self):
        self.assertNotEquals(lnk, Link(config1_path))
        #check to make sure this is a singleton
        self.assertEquals(lnk,
                          Link.instance())

    def test_config_lookup(self):
        lookup = lnk.config('apis.test_api')
        self.assertEquals(lookup, config1['apis']['test_api'])
        self.assertRaises(KeyError, lnk.config, 'this.is.not.a.key')

    def test_fresh(self):
        lookup_conf1 = lnk.config('apis.test_api')
        #now change what config we are pointing to
        lnk.fresh(config_file = config2_path)
        lookup_conf2 = lnk.config('apis.test_api')
        self.assertNotEquals(lookup_conf1, lookup_conf2)
        self.assertEquals(lookup_conf1, config1['apis']['test_api'])
        self.assertEquals(lookup_conf2, config2['apis']['test_api'])

    def test_default_wrapper(self):
        wrap_name = 'apis.test_api'
        api = lnk(wrap_name)
        self.assertEquals(api.wrap_name, wrap_name)
        self.assertEquals(api.user, lnk.config('apis.test_api.user'))
        self.assertEquals(api.password, lnk.config('apis.test_api.password'))
    
    def test_wrapper_not_configured(self):
        self.assertRaises(Exception, lnk, 'this.is.not.a.key')

    def test_wrapper_kwargs_override(self):
        wrap_name = 'apis.test_api'
        user_override = 'this is the overridden user'
        api = lnk(wrap_name, user=user_override)
        self.assertEquals(api.wrap_name, wrap_name)
        self.assertEquals(api.user, user_override)
        self.assertEquals(api.password, lnk.config('apis.test_api.password'))


class TestWrapper(unittest.TestCase):
    pass

if __name__ == '__main__':
    import nose
    nose.runmodule(argv=[__file__,'-vvs','-x','--pdb', '--pdb-failure'],
                   exit=False)
        


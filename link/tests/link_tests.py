import unittest
import os

from link import lnk
from link.wrappers import Wrapper
from link._utils import load_json_file
from link.tests import *

DIR = os.path.dirname(__file__)
TEST_CONFIG = 'test_link.test_config' 
TEST_CONFIG2 = 'test_link2.test_config'
BAD_CONFIG = 'bad_config.test_config'
NO_CONFIG = 'no_config.test_config'

#load in all the configs that we want
CONFIG1 = load_tst_config(TEST_CONFIG)
CONFIG1_PATH = tst_config_path(TEST_CONFIG)
CONFIG2 = load_tst_config(TEST_CONFIG2)
CONFIG2_PATH = tst_config_path(TEST_CONFIG2)
BAD_CONFIG_PATH = tst_config_path(BAD_CONFIG)
#this does not exist
NO_CONFIG_PATH = tst_config_path(NO_CONFIG)

FAKE_WRAPPER_PATH1 = tst_file_path('fake_wrappers')
FAKE_WRAPPER_PATH2 = tst_file_path('fake_wrappers.fake_wrap2')
FAKE_WRAPPER_PACKAGE1 = 'fake_wrappers'
FAKE_WRAPPER_PACKAGE2 = 'fake_wrappers.fake_wrap2'

class TestLink(unittest.TestCase):

    def setUp(self):
        #reset the config every time to config1
        lnk.refresh(config_file=CONFIG1_PATH)

    def test_config(self):
        self.assertEquals(lnk.config(), CONFIG1)

    def test_config_lookup(self):
        lookup = lnk.config('apis.test_api')
        self.assertEquals(lookup, CONFIG1['apis']['test_api'])
        self.assertRaises(KeyError, lnk.config, 'this.is.not.a.key')

    def test_refresh(self):
        lookup_conf1 = lnk.config('apis.test_api')
        #now change what config we are pointing to
        lnk.refresh(config_file = CONFIG2_PATH)
        lookup_conf2 = lnk.config('apis.test_api')
        self.assertNotEquals(lookup_conf1, lookup_conf2)
        self.assertEquals(lookup_conf1, CONFIG1['apis']['test_api'])
        self.assertEquals(lookup_conf2, CONFIG2['apis']['test_api'])
    
    def test_bad_config(self):
        #we want to make sure it won't bomb out on the fresh but 
        #throws exception when you actually do something where it calls the
        #config
        self.assertRaises(ValueError, lnk.refresh, config_file = BAD_CONFIG_PATH)

    def test_no_config(self):
        #we want to make sure that it will load without a config but will throw
        #an appropriate error when you try to use the config
        self.assertRaises(Exception, lnk.refresh, config_file = NO_CONFIG_PATH)

    def test_default_wrapper(self):
        wrap_name = 'apis.test_api'
        api = lnk(wrap_name)
        config = api.config()
        self.assertEquals(api.wrap_name, wrap_name)
        self.assertEquals(config['user'], lnk.config('apis.test_api.user'))
        self.assertEquals(config['password'], lnk.config('apis.test_api.password'))
    
    def test_wrapper_not_configured(self):
        self.assertRaises(Exception, lnk, 'this.is.not.a.key')

    def test_wrapper_kwargs_override(self):
        wrap_name = 'apis.test_api'
        user_override = 'this is the overridden user'
        api = lnk(wrap_name, user=user_override)
        config = api.config()
        self.assertEquals(api.wrap_name, wrap_name)
        self.assertEquals(config['user'], user_override)
        self.assertEquals(config['password'], lnk.config('apis.test_api.password'))

    def test_load_wrapper_directories(self):
        lnk.refresh()
        self.assertEquals(lnk.wrappers, {})
        lnk.load_wrapper_directories([FAKE_WRAPPER_PATH1])
        self.assertTrue(lnk.wrappers.has_key('FakeWrapper'))
        self.assertFalse(lnk.wrappers.has_key('FakeWrapper2'))
        lnk.load_wrapper_directories([FAKE_WRAPPER_PATH2])
        self.assertTrue(lnk.wrappers.has_key('FakeWrapper2'))


class TestLazyFunctions(unittest.TestCase):

    def setUp(self):
        #reset the config every time to config1
        lnk.refresh(config_file=CONFIG1_PATH)

class MockCallableWrapper(Wrapper):
    
    def __init__(self):
        super(MockCallableWrapper, self).__init__()

    @property
    def command(self):
        return 'echo'

class MockNonCallableWrapper(Wrapper):
    
    def __init__(self):
        super(MockNonCallableWrapper, self).__init__()


class TestWrapper(unittest.TestCase):

    def setUp(self):
        lnk.refresh(config_file=CONFIG1_PATH)
        self.wrapper = lnk.test_wrapper
    

if __name__ == '__main__':
    import nose
    nose.runmodule(argv=[__file__,'-vvs','-x','--pdb', '--pdb-failure'],
                   exit=False)
        


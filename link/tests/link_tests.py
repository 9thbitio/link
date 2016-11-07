import unittest
import os
from link import Link, Wrapper
from link.utils import load_json_file
from link.tests import *

from link.exceptions import LNKAttributeException, LNKConfigException

DIR = os.path.dirname(__file__)
TEST_CONFIG = 'test_link.test_config' 
TEST_CONFIG2 = 'test_link2.test_config'
BAD_CONFIG = 'bad_config.test_config'
NO_CONFIG = 'no_config.test_config'

#load in all the configs that we want
lnk = Link.instance()
config1 = load_tst_config(TEST_CONFIG)
config1_path = tst_config_path(TEST_CONFIG)
config2 = load_tst_config(TEST_CONFIG2)
config2_path = tst_config_path(TEST_CONFIG2)
bad_config_path = tst_config_path(BAD_CONFIG)
#this does not exist
no_config_path = tst_config_path(NO_CONFIG)

FAKE_WRAPPER_PATH1 = tst_file_path('fake_wrappers')
FAKE_WRAPPER_PATH2 = tst_file_path('fake_wrappers.fake_wrap2')
FAKE_WRAPPER_PACKAGE1 = 'fake_wrappers'
FAKE_WRAPPER_PACKAGE2 = 'fake_wrappers.fake_wrap2'

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
        self.assertRaises(LNKAttributeException, lnk.config, 'this.is.not.a.key')

    def test_fresh(self):
        lookup_conf1 = lnk.config('apis.test_api')
        #now change what config we are pointing to
        lnk.fresh(config_file = config2_path)
        lookup_conf2 = lnk.config('apis.test_api')
        self.assertNotEquals(lookup_conf1, lookup_conf2)
        self.assertEquals(lookup_conf1, config1['apis']['test_api'])
        self.assertEquals(lookup_conf2, config2['apis']['test_api'])
    
    def test_bad_config(self):
        #we want to make sure it won't bomb out on the fresh but 
        #throws exception when you actually do something where it calls the
        #config
        lnk.fresh(config_file = bad_config_path)
        self.assertRaises(LNKConfigException, lnk.config)

    def test_no_config(self):
        #we want to make sure that it will load without a config but will throw
        #an appropriate error when you try to use the config
        lnk.fresh(config_file = no_config_path)
        self.assertRaises(LNKConfigException, lnk.config)

    def test_default_wrapper(self):
        wrap_name = 'apis.test_api'
        api = lnk(wrap_name)
        config = api.config()
        self.assertEquals(api.wrap_name, wrap_name)
        self.assertEquals(config['user'], lnk.config('apis.test_api.user'))
        self.assertEquals(config['password'], lnk.config('apis.test_api.password'))
    
    def test_wrapper_not_configured(self):
        self.assertRaises(LNKAttributeException, lnk, 'this.is.not.a.key')

    def test_wrapper_kwargs_override(self):
        wrap_name = 'apis.test_api'
        user_override = 'this is the overridden user'
        api = lnk(wrap_name, user=user_override)
        config = api.config()
        self.assertEquals(api.wrap_name, wrap_name)
        self.assertEquals(config['user'], user_override)
        self.assertEquals(config['password'], lnk.config('apis.test_api.password'))

    def test_load_wrapper_directories(self):
        lnk.fresh()
        self.assertEquals(lnk.wrappers, {})
        lnk.load_wrapper_directories([FAKE_WRAPPER_PATH1])
        self.assertTrue(lnk.wrappers.get('FakeWrapper'))
        self.assertFalse(lnk.wrappers.get('FakeWrapper2'))
        lnk.load_wrapper_directories([FAKE_WRAPPER_PATH2])
        self.assertTrue(lnk.wrappers.get('FakeWrapper2'))

    def test_load_wrapper_packages(self):
        lnk.fresh()
        self.assertEquals(lnk.wrappers, {})
        lnk.load_wrapper_packages([FAKE_WRAPPER_PACKAGE1])
        self.assertTrue(lnk.wrappers.get('FakeWrapper'))
        self.assertFalse(lnk.wrappers.get('FakeWrapper2'))
        lnk.load_wrapper_packages([FAKE_WRAPPER_PACKAGE2])
        self.assertTrue(lnk.wrappers.get('FakeWrapper2'))

class TestLazyFunctions(unittest.TestCase):

    def setUp(self):
        #reset the config every time to config1
        lnk.fresh(config_file=config1_path)

    def test_function_lookup(self):
        func = lnk.lazy_functions.test_function
        self.assertTrue(func.commander.has_command("__default__"))
        self.assertTrue(func.commander.has_command("function"))
        self.assertFalse(func.commander.has_command("aeuoaeaosuoesth"))
    
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
        lnk.fresh(config_file=config1_path)
        self.wrapper = lnk.test_wrapper
    
    def test_call(self):
        ran = MockCallableWrapper()('echo')
        self.assertTrue(ran!=None)

    def test_call_default(self):
        ran = MockCallableWrapper()()
        self.assertTrue(ran!=None)
        self.assertRaises(NotImplementedError, MockNonCallableWrapper())


if __name__ == '__main__':
    import nose
    nose.runmodule(argv=[__file__,'-vvs','-x','--pdb', '--pdb-failure'],
                   exit=False)
        


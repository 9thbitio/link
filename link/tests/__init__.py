import unittest
import os
from mock import Mock, MagicMock
from link.utils import load_json_file
from link.common import APIObject

TESTS_DIR = os.path.dirname(__file__)

def tst_file_path(file_name):
    return '%s/%s' % (TESTS_DIR, file_name)

def tst_config_path(config_name):
    return '%s/config/%s' % (TESTS_DIR, config_name)

def tst_db_path(config_name):
    return '%s/dbs/%s' % (TESTS_DIR, config_name)

def load_tst_config(config_name):
    config_path = tst_config_path(config_name)
    return load_json_file(config_path)

class LnkAPITest(unittest.TestCase):
    """
    Has helper functions for making expected return values
    """
    def setUp(self):
        pass
    
    #TODO: Make sure we have other tests to test the APIObject
    def expected(self, message_data=None):
        api_object = APIObject()
        api_object.set_message(message_data)
        return api_object.response


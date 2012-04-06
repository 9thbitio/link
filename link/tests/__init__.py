import unittest
import os
from mock import Mock, MagicMock
from link.utils import load_json_file

TESTS_DIR = os.path.dirname(__file__)

def tst_config_path(config_name):
    return '%s/config/%s' % (TESTS_DIR, config_name)

def load_tst_config(config_name):
    config_path = tst_config_path(config_name)
    return load_json_file(config_path)

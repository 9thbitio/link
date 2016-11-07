import unittest
import json
from mock import Mock, MagicMock
from link.wrappers import APIRequestWrapper, APIResponseWrapper
from xml.etree import cElementTree as ET
import requests


class MockResponse(object):

    def __init__(self):
        self.content = None

class TestResponseWrapper(unittest.TestCase):

    XML = """<!DOCTYPE html>\n<html>\n  <head>\n\t  <title>Whoops - Pivotal Tracker</title>\n    <style type="text/css" media="screen">\n      body {\n        margin: 1em auto 0 auto;\n        width: 30em;\n        padding: 2em 5em;\n        background: white;\n        font-family: Helvetica,sans-serif;\n      }\n      .centered_miniform {\n        border: 3px solid #97C8E5;\n        margin-top: 3em;\n        padding: 3em 4em;\n        color: #333;\n      }\n      a img {\n        border: none;\n      }\n      h1 {\n        font-size: 22px;\n        font-weight: bold;\n      }\n    </style>\n  </head>\n  <body>\n    <a href="/"><img alt="Tracker" src="/images/v7/logos/pivotal_tracker.png" /></a>\n    <div class="centered_miniform">\n      <h1>Whoops, an error occurred</h1>\n      <p>Don\'t worry, we\'re looking into it.</p>\n    </div>\n  </body>\n</html>\n"""

    def setUp(self):
        #this response will be the _wrapped object
        self.response = MockResponse()

    def test_json(self):
        self.response.content = '{"this":"is", "json":true}'
        resp = APIResponseWrapper(response = self.response)
        self.assertEquals(json.loads(self.response.content), resp.json)

    def test_invalid_json(self):
        self.response.content = '{"this:"is", "json":true}'
        resp = APIResponseWrapper(response = self.response)
        #because its a property you have to make it a function
        self.assertRaises(ValueError, lambda: resp.json, )

    def test_xml(self):
        self.response.content = self.XML
        resp = APIResponseWrapper(response = self.response)
        title = resp.xml.getchildren()[0].getchildren()[0].text
        self.assertEquals(title, 'Whoops - Pivotal Tracker')

    def test_invalid_xml(self):
        self.response.content = self.XML[:50]
        resp = APIResponseWrapper(response = self.response)
        self.assertRaises(ValueError, lambda: resp.xml)
        

class TestAPIRequestWrapper(unittest.TestCase):
    
    def setUp(self):
        #override the requests module
        self.requests = MagicMock(spec = requests)
        self.requests.get = MagicMock(spec=requests.get)
        self.requests.post = MagicMock(spec=requests.post)
        self.requests.put = MagicMock(spec=requests.put)
        resp = MagicMock(spec=requests.Response, spec_set=['cookies'])
        resp.cookies  = {}
        self.requests.get.return_value = resp 
        self.requests.post.return_value = resp
        self.requests.put.return_value = resp 
        self.base_url = 'test_base_url'
        self.rw = APIRequestWrapper(base_url=self.base_url, user='test_user',
                                 password='test_password')
        self.rw._wrapped = self.requests

    def test_get(self):
        url_params = '/plus_this_get'
        self.rw.get(url_params=url_params)
        #see what the mock object was called with 
        call_args = self.requests.get.call_args
        #make sure headers get to it ok
        self.assertEquals(call_args[0][0], self.base_url + url_params)
        #self.assertEquals(call_args[1]['headers'], self.rw.headers)

    def test_post(self):
        url_params = '/plus_this_post'
        data = 'this is my data'
        self.rw.post(url_params=url_params, data = data)
        #see what the mock object was called with 
        call_args = self.requests.post.call_args
        #make sure headers get to it ok
        self.assertEquals(call_args[0][0], self.base_url + url_params)
        #self.assertEquals(call_args[1]['headers'], self.rw.headers)
        self.assertEquals(call_args[1]['data'], data)

    def test_put(self):
        url_params = '/plus_this_post'
        data = 'this is my data'
        auth = 'This is auth'
        self.rw.put(url_params=url_params, data = data, auth = auth)
        #see what the mock object was called with 
        call_args = self.requests.put.call_args
        #make sure headers get to it ok
        self.assertEquals(call_args[0][0], self.base_url + url_params)
        #self.assertEquals(call_args[1]['headers'], self.rw.headers)
        self.assertEquals(call_args[1]['auth'], auth)
        self.assertEquals(call_args[1]['data'], data)


if __name__ == '__main__':
    import nose
    nose.runmodule(argv=[__file__,'-vvs','-x','--pdb', '--pdb-failure'],
                   exit=False)
        


from link import APIObject, APIResponse
import json
import unittest

class MockAPIObject(APIObject):

    def __init__(self, message, warnings=None, error=None):
        super(MockAPIObject, self).__init__(message, warnings = warnings, error = error)
    
    def my_message(self):
        return "hello"
    
    @property
    def response_label(self):
        return self.my_label() 

    def my_label(self):
        return "my_response"

    @property
    def message(self):
        """
        Test that we are overriding the message correctly
        """
        return self.my_message()

class TestAPIObject(unittest.TestCase):

    def setUp(self):
        self.message = {'my':'message'}
        self.error = 'error'
        self.warnings = ['my_warnings']

    def test_message_and_warnings(self):
        api = APIObject(self.message, warnings = self.warnings)
        expected = {'response':{'apiobject': self.message}, 'status':'ok',
                    'warnings':self.warnings} 

        self.assertEquals(expected, api.response)
        self.assertEquals(json.dumps(self.message),str(api))

    def test_message(self):
        api = APIObject(self.message)
        expected = {'response':{'apiobject':self.message}, 'status':'ok'}
        self.assertEquals(expected, api.response)
        self.assertEquals(json.dumps(self.message),str(api))

    def test_error(self):
        api = APIObject(self.message, error =self.error)
        expected = {'error':self.error}
        self.assertEquals(expected, api.response)
        self.assertEquals(json.dumps(self.message),str(api))

    def test_message_override(self):
        api = MockAPIObject(self.message)
        expected = {'response':{api.my_label(): api.my_message()}, 'status':'ok'}
        self.assertEquals(expected, api.response)
        self.assertEquals(json.dumps(api.my_message()),str(api))

    def test_message_get_and_get_item(self):
        api = APIObject(self.message)
        self.assertEquals(api.get('my'), self.message.get('my'))
        self.assertEquals(api['my'], self.message['my'])


class MockAPIResponse(APIResponse):

    response_label = 'my_label'

    def __init__(self, message, warnings=None, error=None):
        
        super(MockAPIResponse, self).__init__(message, warnings = warnings, error = error)
    
    def my_message(self):
        return {"hello":"there"}

    @property
    def message(self):
        """
        Test that we are overriding the message correctly
        """
        return self.my_message()


class TestAPIResponse(unittest.TestCase):

    def setUp(self):
        self.message = [{'my':'message'}, {'my2':'message'}]
        self.error = 'error'
        self.warnings = ['my_warnings']

    def test_error(self):
        api = APIResponse(self.message, error =self.error)
        expected = {'error':self.error}
        self.assertEquals(json.dumps(expected), str(api))

    def test_message_and_warnings(self):
        api = APIResponse(self.message, warnings = self.warnings)
        expected = {'response':{api.response_label:self.message}, 'status':'ok',
                    'warnings':self.warnings} 

        self.assertEquals(json.dumps(expected), str(api))

    def test_message(self):
        api = APIResponse(self.message)
        expected = {'response':{api.response_label:self.message}, 'status':'ok'}
        self.assertEquals(json.dumps(expected), str(api))

    def test_message_override(self):
        api = MockAPIResponse(self.message)
        expected = {'response':{api.response_label:api.my_message()},
                                'status':'ok'}
        self.assertEquals(expected, json.loads(str(api)))

    #def test_pagenation(self):
        #message = [1,2,3,4,5,6,7]
        #api = APIResponse(message=message)
        ##default behavior set the number of pages to 50
        #self.assertTrue(api.next_page().message == message)

        #api = APIResponse(message=message)
        #api.pagenate(3)
        #self.assertTrue(api.next_page().message == [1,2,3])
        #self.assertTrue(api.next_page().message == [4,5,6])
        #self.assertTrue(api.next_page().message == [7])



if __name__ == '__main__':
    import nose
    nose.runmodule(argv=[__file__,'-vvs','-x','--pdb', '--pdb-failure'],
                   exit=False)
        


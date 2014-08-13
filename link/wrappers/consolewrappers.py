"""
"""
from link.common import APIResponse
from link.wrappers import APIRequestWrapper, APIResponseWrapper
from requests.auth import AuthBase
import json
import requests


class ConsoleAuth(AuthBase):
    """
    Does the authentication for Console requests.  
    """
    def __init__(self, token):
        # setup any auth-related data here
        self.token = token

    def __call__(self, r):
        # modify and return the request
        r.headers['Authorization'] = self.token
        return r


class ConsoleAPIResponseWrapper(APIResponseWrapper):
    """
    Wraps a response from a console api
    """
    def __init__(self, wrap_name = None, response = None):
        super(ConsoleAPIResponseWrapper, self).__init__(response = response, 
                                                        wrap_name = wrap_name)
    
    @property
    def xml(self):
        """
        This api does not return xml
        """
        raise NotImplementedError('This api does not return xml')
    
    @property
    def error(self):
        """
        Console error is either an error in the wrapper response or
        an error returned by the api in the json
        """
        error = self._wrapped.error
        if error:
            return error

        return self.json['response'].get('error')

    @property
    def error_code(self):
        """
        return the error code 
        """
        return self.json['response'].get('error_code')

    @property
    def error_id(self):
        """
        return the error_id
        """
        return self.json['response'].get('error_code')

    def noauth(self):
        """
        Returns whether erorr is NOAUTH
        """
        try:
            # some endpoints dont return json
            return self.json['response'].get('error_id') == 'NOAUTH'
        except:
            return False
        

class APIClientMessage(object):
    """
    An APIObject could also be a node.  

    The key is really a key_tail.  It does not need to have a hierarchy

    """
    def __init__(self, message = None, warnings = None ,
                error = None):
        self._message = message
        self.error = error
        self.warnings = warnings
        super(APIObject, self).__init__()
    
    @classmethod
    def api_object_name(cls):
        return cls.__name__.lower() 

    #@property 
    #def json(self):
        #return self._json

    def __getitem__(self, name):
        try:
            return self.json[name]
        except:
            raise Exception('no json stored in this APIObject or API Response')

    def __iter__(self):
        return self.json.__iter__()
    
    def get(self, name):
        return self.message.get(name)

    def __str__(self):
        return json.dumps(self.message , cls = APIEncoder)

    def __getitem__(self, key):
        return self.message[key]

    @property
    def response_label(self):
        """
        Only get's called the first time, then it is cached in self.NAME
        """
        return self.api_object_name()

    @property
    def response(self):
        _json = {}

        #if there is an error don't continue
        if self.error:
            _json['error'] = self.error
            return _json
        
        _json['status'] = 'ok'

        if self.message!=None:
            _json['response'] = { self.response_label: self.message }

        if self.warnings:
            _json['warnings'] =  self.warnings

        return _json

    @property
    def message(self):
        return self._message

    def set_message(self, message):
        self._message = message


from link.utils import array_pagenate
import types

class APIClient(APIClientMessage):
    """
    Used to help make standardized Json responses to API's
    """
    def __init__(self, message = None, warnings = None, error = None,
                 seek = None, response_id = None,auth=None):
        super(APIResponse, self).__init__(message, error = error,
                                        warnings = warnings)
        if seek:
            self.seek(*seek)

        self._pages = None

        if auth and isinstance(types.FunctionType):
            #if its a function call then call it and set that to auth
            self.auth = auth()
            
        #let's try this out and see if its any good. 
        #each response get's a unique uuid
        self.response_id = response_id 

    def auth(self):
        raise NotImplementedError()
    
    def seek(self, *kargs):
        raise NotImplementedError()

    #def __getitem__(self, key):
        #return self.response[key]
    
    #def get(self, key):
        #return self.response.get(key)
 
    #def iteritems(self):
        #return self.message.iteritems()

    def __str__(self):
        return json.dumps(self.response, cls = APIEncoder)
    
    def pagenate(self, per_page=100):
        """
        Returns you an iterator of this response chunked into 
        """
        #TODO: need a test for this
        self._pages = array_pagenate(per_page, self.message)

    def next_page(self):
        """
        Returns the next page that is in the generator
        """
        if not self._pages:
            self.pagenate()

        #this is sorta weird, but you want to make that object's message just be
        #next one in the list. Remove the Nones.  There is probably a way to
        #make it so it doesn't have to pad
        try:
            next = self._pages.next() 
        except StopIteration as e:
            #if we are done then set the message to nothing
            self.set_message([])
            return self

        message = [x for x in next if x !=None] 
        self.set_message(message)
        #TODO: need a test for this
        return self

    @property
    def response(self):
        _json = {}

        #if there is an error don't continue
        if self.error:
            _json['error'] = self.error
            return _json
        
        _json['status'] = 'ok'

        if self.message!=None:
            _json['response'] = { self.response_label: self.message }

        if self.warnings:
            _json['warnings'] =  self.warnings

        if self.response_id:
            _json['response_id'] = self.response_id

        return _json


class ConsoleClient(APIClient):

    def __init__(self, wrap_name, base_url, user,password):
        self.api = ConsoleAPIRequestWrapper(wrap_name = wrap_name, base_url=
                                            base_url, user = user, password =
                                            password)

        if not self.check_token():
            raise Exception("Unable to login to the Console API")
       
    def check_token(self):
        """
        checks the token of the api

        :returns: True if the token passes 

        """
        try:
            if self.api.token:
                #TODO: There is a better check than it's there
                return True
        except:
            raise Exception("No auth token found on the authentication") 

        return False


class ConsoleAPIRequestWrapper(APIRequestWrapper):
    """
    Wrap the Console API
    """
    def __init__(self, wrap_name=None, base_url=None, user=None, password=None):
        self._token = None
        super(ConsoleAPIRequestWrapper, self).__init__(wrap_name = wrap_name, 
                                                       base_url=base_url,
                                                       user=user,
                                                       password=password,
                                                       response_wrapper = 
                                                       ConsoleAPIResponseWrapper)
    def authenticate(self):
        """
        Write a custom auth property where we grab the auth token and put it in 
        the headers
        """
        auth_json={'auth':{'username':self.user, 'password':self.password}}
        self._wrapped = requests.session()
        #send a post with no auth. prevents an infinite loop
        auth_response = self.post('/auth', data = json.dumps(auth_json), auth =
                                 None)

        _token =  auth_response.json['response']['token']

        self._token = _token
        self._wrapped.auth = ConsoleAuth(_token) 

    @property
    def token(self):
        """
        Returns the token from the api to tell us that we have been logged in
        """
        if not self._token:
            self._token = self.authenicate().token

        return self._token




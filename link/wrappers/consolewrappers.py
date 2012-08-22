"""
"""
from link.wrappers import APIRequestWrapper, APIResponseWrapper
from requests.auth import AuthBase
import json


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
        

class ConsoleAPIRequestWrapper(APIRequestWrapper):
    """
    Wrap the Console API
    """
    def __init__(self, wrap_name=None, base_url=None, user=None, password=None):
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
        #send a post with no auth. prevents an infinite loop
        auth_response = self.post('/auth', data = json.dumps(auth_json), auth =
                                 None)
        token = auth_response.json['response']['token']
        return ConsoleAuth(token) 



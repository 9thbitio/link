"""
"""
from link.common import APIResponse
from link.wrappers import APIRequestWrapper, APIResponseWrapper
from requests.auth import AuthBase
import json
import requests


class SpringAuth(AuthBase):
    """
    Does the authentication for Spring requests.  
    """
    def __init__(self, token):
        # setup any auth-related data here
        self.token = token

    def __call__(self, r):
        # modify and return the request
        r.headers['Authorization'] = self.token
        return r


class SpringServeAPIResponseWrapper(APIResponseWrapper):
    """
    Wraps a response from the springserve api
    """
    def __init__(self, wrap_name = None, response = None):
        super(SpringServeAPIResponseWrapper, self).__init__(response = response, 
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
        Spring error is either an error in the wrapper response or
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
        


class SpringServeAPI(APIRequestWrapper):
    """
    Wrap the Spring API
    """
    headers = { "Content-Type": "application/json" }

    def __init__(self, wrap_name=None, base_url=None, user=None, password=None):
        self._token = None
        super(SpringServeAPI, self).__init__(wrap_name = wrap_name, 
                                                       base_url=base_url,
                                                       user=user,
                                                       password=password,
                                                       response_wrapper = 
                                                       SpringServeAPIResponseWrapper)

    def authenticate(self):
        """
        Write a custom auth property where we grab the auth token and put it in 
        the headers
        """
        #it's weird i have to do this here, but the code makes this not simple
        auth_json={'email':self.user, 'password':self.password}
        #send a post with no auth. prevents an infinite loop
        auth_response = self.post('/auth', data = json.dumps(auth_json), auth =
                                 None)

        _token =  auth_response.json['token']

        self._token = _token
        self._wrapped.auth = SpringAuth(_token) 

    @property
    def token(self):
        """
        Returns the token from the api to tell us that we have been logged in
        """
        if not self._token:
            self._token = self.authenicate().token

        return self._token




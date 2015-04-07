"""
"""
import hashlib
import json
import requests

from link.common import APIResponse
from link.wrappers import APIRequestWrapper, APIResponseWrapper
from requests.auth import AuthBase


class LiveRailAuth(AuthBase):
    """
    Does the authentication for Console requests.  
    """
    def __init__(self, token):
        # setup any auth-related data here
        self.token = token

    def __call__(self, request):
        # modify and return the request
        url = request.url.split('?')

        # put the api token in the actually request
        if request.body:
            request.body += "&token={}".format(self.token)
        else:
            request.body = "&token={}".format(self.token)
        
        params = {'token':self.token}
        if len(url)>1:
            existing_params = dict([x.split('=') for x in url[1].split("&")])
            params.update(existing_params)
        
        params = "&".join(["{}={}".format(x, y) for x,y in params.iteritems()])

        request.url = "{}?{}".format(url[0], params)
        
        return request


class LiveRailResponseWrapper(APIResponseWrapper):
    """
    Wraps a response from a console api
    """
    def __init__(self, wrap_name = None, response = None):
        super(LiveRailResponseWrapper, self).__init__(response = response, 
                                                        wrap_name = wrap_name)
    
    @property
    def json(self):
        """
        This api does not return xml
        """
        raise NotImplementedError('This api does not return json')
    
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




class LiveRailRequest(APIRequestWrapper):
    """
    Wrap the Console API
    """
    def __init__(self, wrap_name=None, base_url=None, user=None, password=None):
        self._token = None
        super(LiveRailRequest, self).__init__(wrap_name = wrap_name, 
                                                       base_url=base_url,
                                                       user=user,
                                                       password=password,
                                                       response_wrapper = 
                                                       LiveRailResponseWrapper)
    def authenticate(self):
        """
        Write a custom auth property where we grab the auth token and put it in 
        the headers
        """

        hash = hashlib.md5()
        hash.update(self.password)
        auth_payload = {'username':self.user, 'password':hash.hexdigest()}

        self._wrapped = requests.session()

        #send a post with no auth. prevents an infinite loop
        auth_response = self.post('/login', data = auth_payload, auth = None)
        
        try:
            _token =  auth_response.xml.find('.auth/token').text
        except:
            raise Exception("Authentication failed")

        self._token = _token
        self._wrapped.auth = LiveRailAuth(_token) 

    @property
    def token(self):
        """
        Returns the token from the api to tell us that we have been logged in
        """
        if not self._token:
            self._token = self.authenicate().token

        return self._token

    def logout(self):
        return self.get('/logout')



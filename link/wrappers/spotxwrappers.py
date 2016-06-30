
from link.common import APIResponse
from link.wrappers import APIRequestWrapper, APIResponseWrapper
from requests.auth import AuthBase
import json
import requests

class SpotxAuth(AuthBase):
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


class SpotxAPIResponse(APIResponseWrapper):
    pass


class SpotxAPI(APIRequestWrapper):
    """
    Wrap the Console API
    """
    def __init__(self, wrap_name=None, base_url=None, client_id=None,
                 client_secret=None, refresh_token=None, code=None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.refresh_token = refresh_token
        self.code = code
        super(SpotxAPI, self).__init__(wrap_name = wrap_name, 
                                       base_url = base_url,
                                        response_wrapper = SpotxAPIResponse)
    
    def authenticate(self):

        auth_json= {
            'client_id': self.client_id, 
            'client_secret': self.client_secret, 
            'code': self.code, 
            'grant_type': 'authorization_code'
        }

        self._wrapped = requests.session()
        #send a post with no auth. prevents an infinite loop
        auth_response = self.post('/token', data = auth_json, auth =
                                 None)
        
        import pdb; pdb.set_trace()
        if not auth_response.ok or auth_response.json.get('value'):
            raise Exception("Issue authenticating")
       
        info = auth_response.json['value']['data']
        token_type = info['token_type']
        access_token = info['access_token'] 

        self._token = "{} {}".format(token_type, access_token) 
        self._wrapped.auth = SpotxAuth(self._token) 




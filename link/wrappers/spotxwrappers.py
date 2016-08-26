
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
                 client_secret=None, access_token=None, refresh_token=None, 
                 token_type=None, redis_host=None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.refresh_token = refresh_token
        self.access_token = access_token
        self.token_type = token_type
        self.redis_host = redis_host
        super(SpotxAPI, self).__init__(wrap_name = wrap_name, 
                                       base_url = base_url,
                                        response_wrapper = SpotxAPIResponse)
    
    def get_tokens(self):

        import redis
        r = redis.StrictRedis(host=self.redis_host)
        self.refresh_token = r.hget('spotx_tokens', 'refresh_token')
        self.access_token = r.hget('spotx_tokens', 'access_token')
        self.token_type = r.hget('spotx_tokens', 'token_type')

    def authenticate(self):
        self.get_tokens()
        self._token = "{} {}".format(self.token_type, self.access_token)
        self._wrapped.auth = SpotxAuth(self._token)

        if self.get("/Publishers").json['error']['code'] == 'SYSTEM.SERVICE.NOT_AUTHORIZED':
            self.refresh()

    def refresh(self):

        refresh_json= {
            'client_id': self.client_id, 
            'client_secret': self.client_secret, 
            'refresh_token': self.refresh_token, 
            'grant_type': 'refresh_token'
        }

        self._wrapped = requests.session()

        #send a post with no auth. prevents an infinite loop
        refresh_response = self.post('/token', data = refresh_json)
        
        # import pdb; pdb.set_trace()
        if not refresh_response.ok or not refresh_response.json.get('value'):
            raise Exception("Issue Refreshing")
       
        info = refresh_response.json['value']['data']
        self.token_type = info['token_type']
        self.access_token = info['access_token'] 
        # self.refresh_token = info['refresh_token']
        
        self.reset_redis_tokens()

    def reset_redis_tokens(self):

        import redis
        tokens = {
            'access_token' : self.access_token,
            'refresh_token' : self.refresh_token,
            'token_type' : self.token_type
        }

        r = redis.StrictRedis(host=self.redis_host)
        r.hmset('spotx_tokens', tokens)



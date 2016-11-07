
from .apiwrappers import APIRequestWrapper
from requests.auth import AuthBase

class CrucbileAuth(AuthBase):
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


class Crucible(APIRequestWrapper):
    """
    Wraps the Crucible API
    """
    def authenticate(self):
        """
        Write a custom auth property where we grab the auth token and put it in 
        the headers
        """
        #send a post with no auth. prevents an infinite loop
        self.get('/rest-service/auth-v1/login?userName=%spassword=%s' %
                  (self.user, self.password), auth = None)


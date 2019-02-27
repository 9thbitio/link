from requests.auth import AuthBase

from link.wrappers import APIRequestWrapper


class MoatAuth(AuthBase):
    
    def __init__(self, token):
        self.token = token

    def __call__(self, request):
        request.headers['Authorization'] = "Bearer {}".format(self.token)
        request.headers['Content-Type'] = 'application/json'
        return request


class MoatAPI(APIRequestWrapper):

    def authenticate(self):
        self._wrapped.auth = MoatAuth(self.password)

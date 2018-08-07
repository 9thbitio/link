import requests
from requests.auth import AuthBase

from link.wrappers import APIRequestWrapper, APIResponseWrapper


class ForensiqAuth(AuthBase):

    def __init__(self, access_token):
        self.access_token = access_token

    def __call__(self, request):
        request.headers['Authorization'] = 'Bearer {}'.format(self.access_token)
        request.headers['Content-Type'] = 'application/json'
        return request


class ForensiqAPIResponseWrapper(APIResponseWrapper):

    FORENSIQ_UNAUTHED_ERROR_MSG = 'OAuth2 authentication required'
    FORENSIQ_EXPIRED_AUTH_ERROR_MSG = 'The access token provided has expired.'
    FORENSIQ_NOAUTH_ERRORS = (FORENSIQ_UNAUTHED_ERROR_MSG, FORENSIQ_EXPIRED_AUTH_ERROR_MSG)

    def __init__(self, wrap_name=None, response=None):
        super(ForensiqAPIResponseWrapper, self).__init__(response=response,
                wrap_name=wrap_name)

    def noauth(self):
        try:
            return self.json['error_description'] in self.FORENSIQ_NOAUTH_ERRORS
        except:
            return False


class ForensiqAPI(APIRequestWrapper):

    _FIRST_AUTH_GRANT_TYPE = "password"
    _REAUTH_GRANT_TYPE = "refresh_token"

    def __init__(self, wrap_name=None, base_url=None, user=None, password=None,
            client_id=None, client_secret=None):
        # super init calls authenticate(), so these need to be defined first
        self.refresh_token = None
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None

        super(ForensiqAPI, self).__init__(wrap_name=wrap_name, base_url=base_url,
                user=user, password=password, response_wrapper=ForensiqAPIResponseWrapper)

    def authenticate(self):
        auth_data = None
        if self.refresh_token is None:
            auth_data = self._first_auth_params()
        else:
            auth_data = self._reauth_params()

        auth_response = self.post("/oauth/v2/token", data=auth_data, auth=None)

        self.access_token = auth_response.json['access_token']
        self.refresh_token = auth_response.json['refresh_token']

        self._wrapped.auth = ForensiqAuth(self.access_token)

    def _first_auth_params(self):
        auth_data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": self._FIRST_AUTH_GRANT_TYPE,
            "username": self.user,
            "password": self.password,
            "redirect_uri": ""
        }
        return auth_data

    def _reauth_params(self):
        reauth_data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": self._REAUTH_GRANT_TYPE,
            "refresh_token": self.refresh_token
        }
        return reauth_data


import requests
from requests.auth import AuthBase

from link.wrappers import APIRequestWrapper, APIResponseWrapper


class ForensiqImpactAPI(APIRequestWrapper):

    def __init__(self, wrap_name=None, base_url=None, user=None, password=None,
            client_id=None, client_secret=None):
        super(ForensiqImpactAPI, self).__init__(wrap_name=wrap_name, base_url=base_url,
                user=user, password=password)

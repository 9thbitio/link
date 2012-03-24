"""
apilink contains all of the classes that you need to connect to a configured
api.  It wraps the python requests package, and provides some helpful functions
that make it easy to parse json and xml responses
"""
import requests
from requests.auth import HTTPBasicAuth
import json
from xml.etree import cElementTree as ET
from vlinks import Linker, Wrapper

class ResponseWrapper(Wrapper):
    """
    Wrap an API response and make it easy to parse out
    json or XML
    """
    def __init__(self, response, wrap_name = None):
        self.response = response
        self._json = None
        self._xml = None
        self._wrapped = response
        super(ResponseWrapper, self).__init__(wrap_name)

    @property
    def json(self):
        """
        json's the content and returns it as a dictionary
        """
        if not self._json:
            try:
                self._json = json.loads(self.content)
            except:
                raise Exception("Response is not valid json %s " % self.content)
        return self._json

    @property
    def xml(self):
        """
        json's the content and returns it as a dictionary
        """
        if not self._xml:
            try:
                self._xml = ET.XML(self.content)
            except:
                raise Exception("Response is not valid xml %s " % self.content)
        return self._xml

    def tostring(self):
        """
        If you have parsed json or xml it will
        return the manipulated object as a string.  Might not be a very helpful
        function
        """
        if self._json:
            return json.dumps(self._json)

        if self._xml:
            return ET.tostring(self._xml)


class RequestWrapper(Wrapper):
    """
    Wraps the requests class so that all you have to give is
    extra url parameters for it to work fine
    """
    def __init__(self, wrap_name=None, base_url=None, auth=None, user=None, password=None):
        self.base_url = base_url
        self.user = user
        self.password = password

        #if they are authing make the auth object.  Can make the Auth thing a
        #special type of class
        self.auth = auth
        if user and password:
            self.auth = HTTPBasicAuth(user, password)

        self.headers = requests.defaults.defaults['base_headers']

    def request_decorator(func):
        """
        Send a request by the name.  Nice helper function to getattr
        """
        def request_function(self, url_params,  **kwargs):
            return self.request(func.__name__, url_params=url_params,  **kwargs)

        return request_function

    def request(self, method='get', url_params = '' , data = ''):
        """
        Make a request.  This is taken care af by the request decorator
        """
        if isinstance(url_params, dict):
            #tricky, if its a dictonary turn it into a & delimited key=value
            url_params = '&'.join([ '%s=%s' % (key, value) for key,value
                                   in url_params.items()])

        full_url = self.base_url + url_params
        #turn the string method into a function name
        method = requests.__getattribute__(method)
        return ResponseWrapper(method(full_url, auth = self.auth,
                                        headers = self.headers, data = data))

    @request_decorator
    def get(self, url_params = ''):
        pass

    @request_decorator
    def put(self, url_params='', data=''):
        pass

    @request_decorator
    def post(self, url_params='', data=''):
        pass

    def add_to_headers(self, key, value):
        self.headers[key] = value


class APILink(Linker):
    """
    The linked API handler which gives you access to all of your configured
    API's.  It will return an APIWrapper
    """
    def __init__(self):
        super(APILink, self).__init__('apis', RequestWrapper)


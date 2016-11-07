from .apiwrappers import APIRequestWrapper, APIResponseWrapper
from requests.auth import AuthBase
from xml.etree import cElementTree as ET
import base64
import datetime
import hashlib
import hmac
import urllib
import xmltodict

#class AlexaAuth(AuthBase):
    #"""
    #Does the authentication for Console requests.  
    #"""
    #def __init__(self, host, path, access_key, secret_key):
        ## setup any auth-related data here
        #self.host = host
        #self.path = path
        #self.access_key = access_key
        #self.secret_key = secret_key

    #def __call__(self, req):
        ## modify and return the request
        #parameters = self.get_parameters(req.params) 
        #req.url='%s/?%s' % (req.url.rstrip('/'), parameters)
        #return req

    #def sign(self, params):
        #msg = "\n".join(["GET",
                         #self.host,
                         #self.path,
                         #self._urlencode(params)])
        #hmac_signature = hmac.new(str(self.secret_key), msg, hashlib.sha1)
        #signature = base64.b64encode(hmac_signature.digest())
        #return signature

    #def get_parameters(self, params):
        #params.update({
            #"AWSAccessKeyId": self.access_key,
            #"SignatureMethod": "HmacSHA1",
            #"SignatureVersion": 2,
            #"Timestamp": self._get_timestamp(),
        #})
        #params["Signature"] = self.sign(params)
        #return self._urlencode(params)

    #def _get_timestamp(self):
        #return datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z")

    #def _urlencode(self, params):
        #params = [(key, params[key]) for key in sorted(params.keys())]
        #return urllib.urlencode(params)



class AlexaResponse(APIResponseWrapper):
    """
    Wraps a response from the alexa api

    Attributes:
        : @todo description
    """

    def __init__(self, wrap_name = None, response = None):
        super(AlexaResponse,self).__init__(wrap_name =wrap_name,
                                           response=response)

    @property
    def xml(self):
        # returns an ordered dict
        alexa_dict = xmltodict.parse(self.content.replace("aws:",""))
        status_code = alexa_dict['UrlInfoResponse']['Response']['ResponseStatus']['StatusCode']

        # check if there is valid alexa info; if so, return from there onwards
        if status_code == "Success":
          alexa_data = alexa_dict['UrlInfoResponse']['Response']['UrlInfoResult']['Alexa']
          return alexa_data

        return None

class AlexaAPI(APIRequestWrapper):
    """
    Creates and requests different things from the Amazon Alexa API.  This api
    will tell you information about domains

    Sample Get::

        http://awis.amazonaws.com/?
            AWSAccessKeyId=9876543212345123 &
            Action=UrlInfo &ResponseGroup=Rank &
            SignatureMethod=HmacSHA1 &
            SignatureVersion=2 &
            Timestamp=2011-05-06T17%3A58%3A49.463Z &
            Url=yahoo.com &
            Signature=Wz2UT%2BtCYZghLBmqtkfEpg%2FqrK8%3D
    """
    def __init__(self, wrap_name=None, base_url=None, user=None,
                 access_key=None, secret_key = None,
                response_wrapper = AlexaResponse ):
        self.access_key = access_key 
        self.secret_key = secret_key
        super(AlexaAPI, self).__init__(wrap_name=wrap_name, base_url = base_url,
                                       response_wrapper = response_wrapper)
        
    #def authenticate(self):
        #"""
        #Write a custom auth property where we grab the auth token and put it in 
        #the headers
        #"""
        #I don't like this
        #return AlexaAuth(self.base_url.lstrip('http://').rstrip('/'), 
                         #"/", self.access_key, self.secret_key) 
    
    def get_url(self, url_path='/', params=None):
        parameters = self.get_parameters(url_path, params) 
        url='%s?%s' % (url_path, parameters)
        return url

    def sign(self, url_path, params):
        msg = "\n".join(["GET",
                         self.base_url.lstrip('http://').rstrip('/'),
                         url_path,
                         self._urlencode(params)])
        hmac_signature = hmac.new(str(self.secret_key), msg, hashlib.sha1)
        signature = base64.b64encode(hmac_signature.digest())
        return signature

    def get_parameters(self, url_path, params):
        params = params or {}
        params.update({
            "AWSAccessKeyId": self.access_key,
            "SignatureMethod": "HmacSHA1",
            "SignatureVersion": 2,
            "Timestamp": self._get_timestamp(),
        })
        params["Signature"] = self.sign(url_path, params)
        return self._urlencode(params)

    def _get_timestamp(self):
        return datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z")

    def _urlencode(self, params):
        params = [(key, params[key]) for key in sorted(params.keys())]
        return urllib.urlencode(params)


    def url_info(self, urls, response_groups):

        params = { "Action": "UrlInfo" }
        response_groups = ','.join(response_groups)

        if isinstance(urls, str):
            urls = urllib.quote(urls)
            params.update({
                "Url": urls,
                "ResponseGroup": response_groups,
             })

        else:
            urls = map(urllib.quote, urls)
            if len(urls) > 5:
                raise RuntimeError("Maximum number of batch URLs is 5.")

            params.update({ "UrlInfo.Shared.ResponseGroup": response_groups, })    
            
            for i, url in enumerate(urls):
                params.update({"UrlInfo.%d.Url" % (i + 1): url})
        
        return self.get(self.get_url(params=params))



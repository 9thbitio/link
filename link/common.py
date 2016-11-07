from __future__ import absolute_import
import json

#class Node(object):
    #"""
    #This is a node for your data
    #"""
    #def __init__(self, data = None, key=None, hierarchy = None, rules = None):
        #self.key = key 

        #self.hierarchy = hierarchy
        #if hierarchy == None:
            #self.hierarchy = []

        #self.data = data
        #super(Node, self).__init__()

    #def apply(self):
        #pass

class Cacheable(object):
    """
    on object that has a cache built into it for storing data
    """
    def __init__(self, read_permissions = None, write_permissions = None):
        """
        Read permissions is whether the user has read or write access to this db
        Not sure if this will ever be helpful
        """
        super(Cacheable, self).__init__()
        self.cache = {}

    def cache_put(self, key, data, read_type = None):
        """
        Put <key> into the cache into the cache.  If Link is configured to it
        will put it into the end datastore.  Will also make sure that it has
        clean data before writing::
            
            key: the key that you want to store data at
            data: the data that you want to cache
        """
        self.cache[key] = data

    def cache_get(self, key, read_type = None):
        """
        will get the key from the cache.  You can make it so that it will go to
        the underlying database. Takes care of dirty data for
        you...somehow...figure out how to do that 

            key: the key of the data you want to look up in cache
        """
        return self.cache.get(key)

    
#class Result(Node):
    #"""
    #A result of a rule being applied to the data
    #"""
    #def __init__(self, result, data=None, actions=None, key=None, hierarchy=None):
        #self.result = result
        #self.data = data
        #self.actions = actions
        #super(Result, self).__init__(key, hierarchy)

#class Rule(object):
    #"""
    #A rule is applied to data and if a row of data passes then the actions are
    #taking actions are 
    #"""

    #def __init__(self, data = None, results= None):
        #self.data = data
        #self.actions = actions

class Single(object):
    """
    Creates a singleton
    """
    _instance = None
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Single, cls).__new__(
                cls, *args, **kwargs)
        return cls._instance

#class Data(Single, Cacheable):
    #"""
    #Encapsulates data from a database
    #"""
    #def __init__(self, data = None,query = None, table = None):
        #self.table = table
        #self.data = data
        #self.query = query
        #super(Data, self).__init__()

    #def __call__(self):
        #print self.table
        #print self.data
        #print self.query

    #def __iter__(self):
        #"""
        #If it's never set then throw an exception
        #"""
        #if self.data == None:
            #raise Exception("No data to iterate through")

        #return self.data.__iter__()

#class DataSet(Single, Cacheable):
    #"""
    #Encapsulates data from a database
    #"""
    #def __init__(self, data = None):
        #self.data = data
        #super(Data, self).__init__()
    
    #def __call__(self):
        #pass

    #def cache_get(self):
        #pass

    #def __iter__(self):
        #"""
        #If it's never set then throw an exception
        #"""
        #if self.data == None:
            #raise Exception("No data to iterate through")

        #return self.data.__iter__()

    #def refresh(self):
        #"""
        #A function that allows you to refresh a full dataset.  
        #"""
        #pass

#class Action(object):
    #pass

#class Actions(object):

    #def __init__(self, actions = None, query = None, table = None):
        #self.actions = actions
        #self.table = table
        #self.query = query
        #super(Actions, self).__init__()

import datetime

class APIEncoder(json.JSONEncoder):
    """
    The json encoder we will use for our APIs
    """

    def default(self, obj):
        #Need to do type == not isinstance()
        if isinstance(obj, APIObject):
            if isinstance(obj, APIResponse):
                return obj.response
            return obj.message
        
        #we will use the default format...but we probably want to make this
        #configurable
        if isinstance(obj, datetime.datetime):
            return str(obj)

        return super(APIEncoder, self).encode(obj)

    def encode(self, obj):
        return super(APIEncoder, self).encode(obj)


class APIObject(object):
    """
    An APIObject could also be a node.  

    The key is really a key_tail.  It does not need to have a hierarchy

    """

    def __init__(self, message = None, warnings = None ,
                error = None):
        self._message = message
        self.error = error
        self.warnings = warnings
        super(APIObject, self).__init__()
    
    @classmethod
    def api_object_name(cls):
        return cls.__name__.lower() 

    #@property 
    #def json(self):
        #return self._json

    def __getitem__(self, name):
        try:
            return self.json[name]
        except:
            raise Exception('no json stored in this APIObject or API Response')

    def __iter__(self):
        return self.json.__iter__()
    
    def get(self, name):
        return self.message.get(name)

    def __str__(self):
        return json.dumps(self.message , cls = APIEncoder)

    def __getitem__(self, key):
        return self.message[key]

    @property
    def response_label(self):
        """
        Only get's called the first time, then it is cached in self.NAME
        """
        return self.api_object_name()

    @property
    def response(self):
        _json = {}

        #if there is an error don't continue
        if self.error:
            _json['error'] = self.error
            return _json
        
        _json['status'] = 'ok'

        if self.message!=None:
            _json['response'] = { self.response_label: self.message }

        if self.warnings:
            _json['warnings'] =  self.warnings

        return _json

    @property
    def message(self):
        return self._message

    def set_message(self, message):
        self._message = message


from .utils import array_pagenate
import types

class APIResponse(APIObject):
    """
    Used to help make standardized Json responses to API's
    """
    def __init__(self, message = None, warnings = None, error = None,
                 seek = None, response_id = None,auth=None):
        super(APIResponse, self).__init__(message, error = error,
                                        warnings = warnings)
        if seek:
            self.seek(*seek)

        self._pages = None

        if auth and isinstance(types.FunctionType):
            #if its a function call then call it and set that to auth
            self.auth = auth()
            
        #let's try this out and see if its any good. 
        #each response get's a unique uuid
        self.response_id = response_id 

    def auth(self):
        raise NotImplementedError()
    
    def seek(self, *kargs):
        raise NotImplementedError()

    #def __getitem__(self, key):
        #return self.response[key]
    
    #def get(self, key):
        #return self.response.get(key)
 
    #def iteritems(self):
        #return self.message.iteritems()

    def __str__(self):
        return json.dumps(self.response, cls = APIEncoder)
    
    def pagenate(self, per_page=100):
        """
        Returns you an iterator of this response chunked into 
        """
        #TODO: need a test for this
        self._pages = array_pagenate(per_page, self.message)

    def next_page(self):
        """
        Returns the next page that is in the generator
        """
        if not self._pages:
            self.pagenate()

        #this is sorta weird, but you want to make that object's message just be
        #next one in the list. Remove the Nones.  There is probably a way to
        #make it so it doesn't have to pad
        try:
            next = self.next_page(self._pages) 
        except StopIteration as e:
            #if we are done then set the message to nothing
            self.set_message([])
            return self

        message = [x for x in next if x !=None] 
        self.set_message(message)
        #TODO: need a test for this
        return self

    @property
    def response(self):
        _json = {}

        #if there is an error don't continue
        if self.error:
            _json['error'] = self.error
            return _json
        
        _json['status'] = 'ok'

        if self.message!=None:
            _json['response'] = { self.response_label: self.message }

        if self.warnings:
            _json['warnings'] =  self.warnings

        if self.response_id:
            _json['response_id'] = self.response_id

        return _json



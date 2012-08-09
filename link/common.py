import json

class Node(object):
    """
    This is a node for your data
    """
    def __init__(self, data = None, key=None, hierarchy = None, rules = None):
        self.key = key 

        self.hierarchy = hierarchy
        if hierarchy == None:
            self.hierarchy = []

        self.data = data
        super(Node, self).__init__()

    def apply(self):
        pass

class Result(Node):
    """
    A result of a rule being applied to the data
    """
    def __init__(self, result, data=None, actions=None, key=None, hierarchy=None):
        self.result = result
        self.data = data
        self.actions = actions
        super(Result, self).__init__(key, hierarchy)

class Rule(object):
    """
    A rule is applied to data and if a row of data passes then the actions are
    taking actions are 
    """

    def __init__(self, data = None, results= None):
        self.data = data
        self.actions = actions

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

class Data(Single):
    """
    Encapsulates data from a database
    """
    def __init__(self, data = None,query = None, table = None):
        self.table = table
        self.data = data
        self.query = query
        super(Data, self).__init__()

    def __call__(self):
        print self.table
        print self.data
        print self.query

    def __iter__(self):
        """
        If it's never set then throw an exception
        """
        if self.data == None:
            raise Exception("No data to iterate through")

        return self.data.__iter__()

class Action(object):
    pass

class Actions(object):

    def __init__(self, actions = None, query = None, table = None):
        self.actions = actions
        self.table = table
        self.query = query
        super(Actions, self).__init__()


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

        return super(APIEncoder, self).encode(obj)

    def encode(self, obj):
        return super(APIEncoder, self).encode(obj)


class APIObject(Node):
    """
    An APIObject could also be a node.  

    The key is really a key_tail.  It does not need to have a hierarchy

    """

    def __init__(self, message = None, warnings = None ,
                error = None, key = None):
        self._message = message
        self.error = error
        self.warnings = warnings
        super(APIObject, self).__init__(json)
    
    @classmethod
    def api_object_name(cls):
        return cls.__name__.lower() 

    @property 
    def json(self):
        return self._json

    def __getitem__(self, name):
        try:
            return self.json[name]
        except:
            raise Exception('no json stored in this APIObject or API Response')

    def __iter__(self):
        return self.json.__iter__()
    
    def get(self, name):
        return self.json.get(name)

    def __str__(self):
        return json.dumps(self.message , cls = APIEncoder)

    def __getitem__(self, key):
        return self.json[key]

    @property
    def response(self):
        _json = {}

        #if there is an error don't continue
        if self.error:
            _json['error'] = self.error
            return _json
        
        _json['status'] = 'ok'

        if self.message!=None:
            _json['response'] = self.message 

        if self.warnings:
            _json['warnings'] =  self.warnings

        return _json

    @property
    def message(self):
        return self._message


class APIResponse(APIObject):
    """
    Used to help make standardized Json responses to API's
    """
    def __init__(self, message = None, warnings = None, error = None, data = None):
        super(APIResponse, self).__init__(message, error = error,
                                        warnings = warnings)

    @property
    def response_label(self):
        """
        Only get's called the first time, then it is cached in self.NAME
        """
        return self.api_object_name()

    def __getitem__(self, key):
        return self.response[key]
    
    def get(self, key):
        return self.response.get(key)
 
    def iteritems(self):
        return self.response.iteritems()

    def __str__(self):
        return json.dumps(self.response, cls = APIEncoder)

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



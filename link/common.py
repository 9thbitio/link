import json

class Node(object):
    """
    This is a node for your data
    """
    def __init__(self, data = None, key=None, hierarchy = None, rules = None):
        self.key = key 
        self.hierarchy = hierarchy 
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
        if isinstance(obj, APIObject):
            return obj.json

        return super(APIEncoder, self).encode(obj)

    def encode(self, obj):

        #if isinstance(obj, APIResponse):
            #obj_new = {}

            #if self.response:
                #obj_new['response'] = self.response

            #if self.error:
                #obj_new['error'] = self.error
            #else:
                #obj_new['status'] = 'ok'

            #if selfwarnings:
                #obj_new['warnings'] =  self.warnings
            
        return super(APIEncoder, self).encode(obj)

class APIObject(Node):
    """
    An APIObject could also be a node.  

    The key is really a key_tail.  It does not need to have a hierarchy

    """
    def __init__(self, json = None, key = None, hierarchy = None ):
        self._json = json
        super(APIObject, self).__init__(json, key, hierarchy)
    
    @property 
    def json(self):
        return self._json

    def __getitem__(self, name):
        try:
            return self.json[name]
        except:
            raise Exception('no json stored in this APIObject or API Response')
    
    def get(self, name):
        return self._json.get(name)

    def __str__(self):
        return json.dumps(self.json, cls = APIEncoder)


class APIResponse(APIObject):
    """
    Used to help make standardized Json responses to API's
    """
    @classmethod
    def api_object(cls):
        cls._name = cls.__name__.lower() 
        return cls._name

    @property
    def _name(self):
        """
        Only get's called the first time, then it is cached in self.NAME
        """
        return self.api_object()

    def __init__(self, response = None, warnings = None, error = None, key = None,
                 hierarchy = None, data = None):
        self._response = response
        self.warnings = warnings
        self.error = error
        super(APIObject, self).__init__(data, key, hierarchy)

    def __getitem__(self, name):
        return self.response[name]

    def __iter__(self):
        return self.response.__iter__()
    
    def iteritems(self):
        return self.response.iteritems()

    @property
    def json(self):
        """
        return the json version of this object
        """
        _json = {}

        if self.response:
            _json['response'] = { self._name: self.response }

        if self.error:
            _json['error'] = self.error
        else:
            _json['status'] = 'ok'

        if self.warnings:
            _json['warnings'] =  self.warnings

        return _json

    @property
    def response(self):
        return self._response

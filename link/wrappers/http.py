#from flask import Flask
from functools import wraps
from link import Wrapper
import json

#app = Flask(__name__)

def response(*kargs, **kwargs):
    return Response(*kargs, **kwargs)

class Response(Wrapper):
    """
    Allows you to decorate a function that is a response so that it has a proper 
    format
    An API style response 
    """
    def __init__(self, routes, methods = ['GET'],  response=None, warnings = None,
                 error = None, wrap_name=None):

        print "here"
        self.routes = routes
        self.methods = methods
        self.response = response

        self.warnings = []
        if isinstance(warnings, str):
           self.warnings.append(warnings)

        self.error = error
        super(Response, self).__init__(wrap_name)

    def __call__(self, func):
        """
        Return a function because this is a decorator
        """
        print func
        print self.__str__
        print self.routes
        @wraps
        #@app.route(self.routes, methods = self.methods)
        def respond(*kargs, **kwargs):
            """
            Gives itself as a parameter so that you can set the return value
            """
            print self.__str__
            print self.response
            #print app.__dict__
            #print func.__name__
            #print kargs
            #print kwargs
            try:
                func(response = self,  **kwargs)
            except Exception as e:
                self.error = "ERROR - %s " % e.message

            return str(self)

        return respond

    def add_warning(self, msg, key = 'WARNING'):
        """
        Add to the warnings a dictionary of warnings
        """
        self.warnings.append(dict(key, msg))

    def add_error(self, msg, key = 'WARNING'):
        """
        Add to the warnings a dictionary of warnings
        """
        self.errors.append({key:msg})
   
    @property
    def dict(self):
        """
        returns it as a dictinory
        """
        response = {}
        if self.response:
            response['response'] = self.response

        if self.warnings:
            response['warnings'] = self.warnings
 
        if self.error:
            response['error'] = self.error
        else:
            response['status'] = 'OK'

        return response
    
    def __str__(self):
        """
        Make the response into a string
        """
        return json.dumps(self.dict) 
    

from link import Wrapper
import json

class Response(Wrapper):
    """
    Allows you to decorate a function that is a response so that it has a proper 
    format
    An API style response 
    """
    def __init__(self, response=None, warnings = None,
                 error = None, wrap_name=None):
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
        def respond(*kargs, **kwargs):
            """
            Gives itself as a parameter so that you can set the return value
            """
            try:
                func(*kargs, response = self,  **kwargs)
            except Exception as e:
                self.error = "ERROR - %s " % e.message

            return self

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
        response = {'response':self.response}

        if self.warnings:
            response['warnings'] = self.warnings
 
        if self.error:
            response['error'] = self.error

        return response
    
    def __str__(self):
        """
        Make the response into a string
        """
        return json.dumps(self.dict) 
    


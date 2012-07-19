from link import Wrapper
import json

class Response(object):
    """
    An API style response 
    """
    def __init__(self, response=None, warnings = None,
                 error = None, wrap_name=None):
        self.response = response

        self.warnings = []
        if isinstance(warnings, str):
           self.warnings.append(warnings)

        self.error = error

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
            response['warnings'] = warnings
 
        if self.error:
            response['error'] = error

        return response

    @property
    def json(self):
        """
        Make the response into a string
        """
        return json.dumps(self.dict) 
    


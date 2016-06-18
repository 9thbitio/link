"""
I don't exactly love that you have to do this.  I will look for a new design
"""
from link import __GET_LINK__

class Wrapper(object):
    """
    The wrapper wraps a piece of the configuration.
    """
    def __init__(self, wrap_name=None, wrapped_object=None, **kwargs):
        super(Wrapper, self).__init__()
        self.wrap_name = wrap_name
        self._wrapped = wrapped_object
        self.loaded = True
        self.cache = {}
        self.__dict__['__link_config__'] = kwargs

    def __getattr__(self, name):
        """
        wrap a special object if it exists
        """
        # first look if the Wrapper object itself has it
        try:
            return self.__getattribute__(name)
        except AttributeError as e:
            pass

        if self._wrapped is not None:
            # if it has a getattr then try that out otherwise go to getattribute
            # TODO: Deeply understand __getattr__ vs __getattribute__.
            # this might not be correct
            try:
                return self._wrapped.__getattr__(name)
            except AttributeError as e:
                try:
                    return self._wrapped.__getattribute__(name)
                except AttributeError as e:
                    raise AttributeError("No Such Attribute in wrapper %s" % name)

        # then it is trying to unpickle itself and there is no setstate
        # TODO: Clean this up, it's crazy and any changes cause bugs
        if name == '__setstate__':
            raise AttributeError("No such attribute found %s" % name)

        # call the wrapper to create a new one
        wrapper = '%s.%s' % (self.wrap_name, name)

        if self.wrap_name:
            return __GET_LINK__(wrapper)

        raise AttributeError("No such attribute found %s" % name)
    
    def __getitem__(self, name):
        return self.__getattr__(name)

    def config(self):
        return self.__link_config__


from apiwrappers import *
from dbwrappers import *
from nosqlwrappers import *
from consolewrappers import *
from springservewrappers import *
from alexawrappers import *
from hivewrappers import *
from elasticsearchwrappers import *

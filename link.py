import os
from utils import json_load_file
from debuglink import DebugLink

debug = DebugLink()

class Mock(object):

    @debug.listen
    def debug_listen(self, function_name, *kargs, **kwargs):
        """
        Lets you listen any wrapper or linker to see what the args are to the function.
        Differs from debug_inspect because it does not do the function call and will not
        give you back the results of the call
        """
        return self.__getattribute__(function_name)(*kargs, **kwargs)

    @debug.inspect
    def debug_inspect(self, function_name, *kargs, **kwargs):
        """
        Lets you listen any wrapper or linker.  Gives you the inputs and results of the function
        """
        return self.__getattribute__(function_name)(*kargs, **kwargs)


class Wrapper(Mock):

    _wrapped = None

    def __init__(self, wrap_name = None, **kwargs):
        self.wrap_name = wrap_name
        self._link = Link.instance()

    def __getattr__(self, name):
        """
        wrap a special object if it exists
        """
        try:
            return self.__getattribute__(name)
        except Exception as e:
            if self._wrapped:
                return self._wrapped.__getattribute__(name)
            raise e

    def run(self):
        pass


class MockWrapper(Wrapper):

    def __init__(self, wrap_name = None):
        super(MockWrapper, self).__init__(wrap_name=wrap_name)


class Link(Mock):
    """
    Link is a singleton that keeps all configuration for the program. It is
    used by any Linked object so that there can be a shared configuration across
    the entire program.  The configuration is stored in json in a file called
    .vlink.config
    """
    __link_instance = None

    GLOBAL_CONFIG = os.path.dirname(os.path.abspath(__file__)) + '/link.config'
    USER_GLOBAL_CONFIG = '%s/.link/link.config' % os.getenv('HOME')

    @classmethod
    def global_config_file(cls):
        """
        Gives you the global config based on the hierchial lookup::

            first check ~/.vlink.config
            then check ./.vlink.config

        """
        #if there is a user global then use that instead of the framework global
        if os.path.exists(cls.USER_GLOBAL_CONFIG):
            return cls.USER_GLOBAL_CONFIG

        return cls.GLOBAL_CONFIG

    @classmethod
    def instance(cls, config_file=None):
        """
        Gives you a singleton instance of the Link object
        which shares your configuration across all other Linked
        objects
        """
        if not config_file:
            config_file = cls.global_config_file()

        if cls.__link_instance:
            return cls.__link_instance

        __link_instance = Link(config_file)
        return __link_instance

    def __init__(self, config_file):
        """
        Create a new instance of the Link.  Should be done
        through the instance() method.
        """
        self.config_file = config_file
        self.__config = json_load_file(config_file)

    @property
    def config(self):
        """
        returns the configuration that is in the Link.  This property
        will allow for us to add more logic later on.
        """
        return self.__config

class Linker(Mock):
    """
    Linked Objects are ones that are linked to the Link
    instance, which carries the global configuration
    for the rest of the program since it is a singleton.  An
    "Link" object shares the state of the program
    """
    def __init__(self, conf_key=None, wrapper_object=Wrapper):
        self._link = Link.instance()
        self.conf_key = conf_key
        self.wrapper_object = wrapper_object

    @property
    def config(self):
        """
        If you have a conf_key then return the
        dictionary of the configuration
        """
        if self.conf_key:
            try:
                return self._link.config[self.conf_key]
            except:
                raise Exception("Nothing configured for %s " % self.conf_key)

        return None

    def configured_links(function):
        """
        gives you a link to your Linked Class.
        pass
        """
        pass

    def linker(func):
        """
        A linker function is one that links your configuration
        to an actual instance of a linked object
        """
        def get_configured_object(self, wrap_name=None, **kwargs):
            """
            calls back the function with a fully wrapped class
            """
            #if they supply a name we want to just create the object from the configuratian and return it
            if not self.conf_key or wrap_name:
                wrap_config = {}
                if wrap_name:
                    wrap_config = self.config[wrap_name]

                try:
                    return self.wrapper_object(wrap_name = wrap_name, **wrap_config)
                except TypeError as e:
                    raise e
                    raise Exception('Wrapper does not except the configured arguments %s' % wrap_config.keys())

            #otherwise jost called the wrapped function
            return self.wrapper_object(**kwargs)

        return get_configured_object

    @linker
    def links(self, wrap = None, **kwargs):
        """
        Returns one or more nosewrapper
        """
        pass

    def __call__(self, wrap_name = None):
        """
        Make it so you can call Linker(wrap) and have that return a link for the
        configured wrap
        """
        return self.links(wrap_name)


class MockLink(Linker):

    def __init__(self):
        super(MockLink, self).__init__('', MockWrapper)



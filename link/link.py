import os
import sys
from utils import load_json_file
from debuglink import DebugLink

debug = DebugLink()

class Mock(object):

    @debug.listen
    def debug_listen(self, function_name, *kargs, **kwargs):
        """
        Lets you listen any wrapper or linker to see what the args are to the
        function.  Differs from debug_inspect because it does not do the 
        function call and will not give you back the results of the call
        """
        return self.__getattribute__(function_name)(*kargs, **kwargs)

    @debug.inspect
    def debug_inspect(self, function_name, *kargs, **kwargs):
        """
        Lets you listen any wrapper or linker.  Gives you the inputs and 
        results of the function
        """
        return self.__getattribute__(function_name)(*kargs, **kwargs)


class Wrapper(Mock):

    _wrapped = None

    def __init__(self, wrap_name = None, wrapped_object=None):
        self.wrap_name = wrap_name
        self._wrapped = wrapped_object
        #self._link = Link.instance()
    
    def __getattr__(self, name):
        """
        wrap a special object if it exists
        """
        try:
            return self.__getattribute__(name)
        except Exception as e:
            if self._wrapped is not None:
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
    def config_file(cls):
        """
        Gives you the global config based on the hierchial lookup::

            first check ~/link.config
            then check ./link.config

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
        if cls.__link_instance:
            return cls.__link_instance

        if not config_file:
            config_file = cls.config_file()
        
        cls.__link_instance = Link(config_file)
        return cls.__link_instance

    def __init__(self, config_file):
        """
        Create a new instance of the Link.  Should be done
        through the instance() method.
        """
        self.config_file = config_file
        self.__config = load_json_file(config_file)
        #i think if you try to set linker = Linker()
        #here it causes an infinite loop
        self.linker = None

    def config(self, config_lookup = None):
        """
        If you have a conf_key then return the
        dictionary of the configuration
        """
        ret = self.__config

        if config_lookup:
            try:
                for value in config_lookup.split('.'):
                    ret = ret[value] 
            except KeyError:
                raise('No such configured object %s' % config_lookup)
            return ret

        return self.__config

    def __call__(self, *kargs, **kwargs):
        if not self.linker:
            self.linker = Linker()
        
        return self.linker(*kargs, **kwargs)

lnk = Link.instance()

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

    def config(self, config_lookup = None):
        """
        If you have a conf_key then return the
        dictionary of the configuration
        """
        ret = self._link.config()

        if config_lookup:
            try:
                for value in config_lookup.split('.'):
                    ret = ret[value] 
            except KeyError:
                raise('No such configured object %s' % config_lookup)
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
        to an actual instance of a linked object.  The key is a '.'
        seperated list of keys to look up in the configuration.  For 
        instance prod.dbs.mydb, it would look up this key in your
        configuration::

            {
            "prod":
                {"dbs":
                    {
                    "mydb":{
                        "host":"<myhost>"
                        ...
                    }
                }
            }
    
        """
        def get_configured_object(self, wrap_name=None, override_config = False, **kwargs):
            """
            calls back the function with a fully wrapped class
            """
            #if they supply a name we want to just create the object 
            #from the configuratian and return it
            if wrap_name:
                wrap_config = self._link.config(wrap_name)
                if not wrap_config:
                    raise Exception('No such key in configuration: %s' 
                                           % wrap_name)

                # if they override the config then
                # update what is in the config with the 
                # parameters passed in
                if override_config:
                    wrap_config.update(kwargs)
                else:
                    kwargs.update(wrap_config)
                    wrap_config = kwargs
    
                # if it is here we want to remove before we pass through
                wrapper = wrap_config.pop('wrapper', None)
                    
                # if they tell us what type it should be then use it
                if wrapper:
                    try:
                        import wrappers
                        wrapper = wrappers.__getattribute__(wrapper)
                    except AttributeError as e:
                        raise Exception('Wrapper cannot be found by the' +
                                        ' link class when loading: %s ' % (wrapper))
                else:
                    wrapper = Wrapper

                try:
                    return wrapper(wrap_name = wrap_name, **wrap_config)
                except TypeError as e:
                    raise Exception('<%s> does not except the configured arguments %s' %
                                    (wrapper, ','.join(wrap_config.keys())))

            #otherwise jost called the wrapped function
            return self.wrapper_object(**kwargs)

        return get_configured_object

    @linker
    def links(self, wrap = None, **kwargs):
        """
        Returns one or more nosewrapper
        """
        pass

    def __call__(self, wrap_name = None, override_config = False, *kargs, **kwargs):
        """
        Make it so you can call Linker(wrap) and have that return a link for the
        configured wrap
        """
        return self.links(wrap_name, *kargs, **kwargs)


class MockLink(Linker):

    def __init__(self):
        super(MockLink, self).__init__('', MockWrapper)


def install_ipython_completers():  # pragma: no cover
    """Register the Panel type with IPython's tab completion machinery, so
    that it knows about accessing column names as attributes."""
    from IPython.utils.generics import complete_object
    import inspect

    @complete_object.when_type(Wrapper)
    def complete_wrapper(obj, prev_completions):
        """
        Add in all the methods of the _wrapped object so its
        visible in iPython as well
        """
        obj_members = inspect.getmembers(obj._wrapped)
        return prev_completions + [c[0] for c in obj_members]

# Importing IPython brings in about 200 modules, so we want to avoid it unless
# we're in IPython (when those modules are loaded anyway).
# Code attributed to Pandas, Thanks Wes 
if "IPython" in sys.modules:  # pragma: no cover
    try:
        install_ipython_completers()
    except Exception:
        pass

import os
import sys
import inspect
from utils import load_json_file
from subprocess import Popen

class Link(object):
    """
    Link is a singleton that keeps all configuration for the program. It is
    used by any Linked object so that there can be a shared configuration across
    the entire program.  The configuration is stored in json in a file called
    .vlink.config
    """
    __link_instance = None

    GLOBAL_CONFIG = os.path.dirname(os.path.abspath(__file__)) + '/config/link.config'
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
    def instance(cls):
        """
        Gives you a singleton instance of the Link object
        which shares your configuration across all other Linked
        objects.  This is called called to create lnk and for the 
        most part should not be called again
        """
        if cls.__link_instance:
            return cls.__link_instance

        cls.__link_instance = Link()
        return cls.__link_instance
    
    def _get_all_wrappers(self, mod_or_package):
        """
        Given a module or package name in returns all
        classes that could possibly be a wrapper in 
        a dictionary
        """
        try:
            wrapper_mod = __import__(mod_or_package, fromlist = ['*'])
        except ImportError as e:
            raise ImportError("No such wrapper in the PYTHONPATH: %s" %
                              e.message)
        #get all classes by name and put them into a dictionary
        wrapper_classes = dict([(name,cls) for name, cls in
                                inspect.getmembers(wrapper_mod) if
                                inspect.isclass(cls)])
        return wrapper_classes

    def load_wrappers(self):
        """
        loads up all the wrappers that can be accessed right now
        """
        #load all the standard ones first
        self.wrappers = self._get_all_wrappers('link.wrappers')
        directories = self.__config.get('external_wrapper_directories')
        self.load_wrapper_directories(directories)
        packages = self.__config.get('external_wrapper_packages')
        self.load_wrapper_packages(packages)
    
    def load_wrapper_directories(self, directories):
        """
        Load in all of the external_wrapper_directories
        """
        if directories:
            for ext_path in directories:
                path_details = ext_path.rstrip('/').split('/')
                #the path we add to sys.path is this without the last word
                path = '/'.join(path_details[:-1])
                mod = path_details[-1]
                #TODO: Need to put an error here if this directory does not 
                # exist
                if path not in sys.path:
                    sys.path.append(path)
                wrapper_classes = self._get_all_wrappers(mod)
                self.wrappers.update(wrapper_classes) 
    
    def load_wrapper_packages(self, packages):
        """
        load in all of the external_wrapper_packages
        """
        #load in all the packages 
        if packages:
            for ext_mod in packages:
                wrapper_classes = self._get_all_wrappers(ext_mod)
                self.wrappers.update(wrapper_classes) 
 
    def fresh(self, config_file=None, namespace=None):
        """
        sets the environment with a fresh config or namespace that is not
        the defaults if config_file or namespace parameters are given
        """
        if not config_file:
            config_file = self.config_file()
 
        self.__config_file = config_file
        self.__config = load_json_file(config_file)
        self.namespace = namespace
        self.wrappers = {}

    def __init__(self, config_file=None, namespace=None):
        """
        Create a new instance of the Link.  Should be done
        through the instance() method.
        """
        #i think if you try to set linker = Linker()
        #here it causes an infinite loop
        self.wrappers = {}
        self.linker = None
        self.fresh(config_file, namespace)
    
    def __getattr__(self, name):
        try:
            return self.__getattribute__(name)
        except Exception as e:
            try:
                return self(wrap_name = name, **self.__config[name].copy())
            except:
                raise Exception('Link has no attribute %s and none is configured'
                                % name)

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
                raise KeyError('No such configured object %s' % config_lookup)
            return ret

        return self.__config

    def __call__(self, *kargs, **kwargs):
        if not self.linker:
            self.linker = Linker()
        
        return self.linker(*kargs, **kwargs)


lnk = Link.instance()


class Wrapper(object):
    """
    The wrapper wraps a piece of the configuration.  
    """
    _wrapped = None

    def __init__(self, wrap_name = None, wrapped_object=None, **kwargs):
        self.wrap_name = wrap_name
        self._wrapped = wrapped_object
        self.__dict__['__link_config__'] = kwargs
        #self._link = Link.instance()
    
    def __getattr__(self, name):
        """
        wrap a special object if it exists
        """
        try:
            if self._wrapped is not None:
                return self._wrapped.__getattribute__(name)
        except:
            raise AttributeError("No Such Attribute in wrapper %s" % name)
        
        wrapper = '%s.%s' % (self.wrap_name, name)
        try:
            if self.wrap_name:
                return lnk(wrapper)
        except Exception as e:
            raise AttributeError("Error creating wrapper %s: %s" % (wrapper,
                                 e.message))

        raise AttributeError("No such attribute found %s" % name)

    def config(self):
        return self.__link_config__

    def run_command(self, cmd):
        p= Popen(cmd,shell=True)
        p.wait()
        return p

    def __call__(self, *kargs, **kwargs):
        """
        by default a wrapper with a __cmd__ will be run on the command line
        """
        cmd = self.config().get('__cmd__')
        if cmd:
            return self.run_command(cmd)
        else:
            print self



class Linker(object):
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
        def get_configured_object(self, wrap_name=None, **kwargs):
            """
            calls back the function with a fully wrapped class
            """
            #if they supply a name we want to just create the object 
            #from the configuratian and return it
            wrap_config = {}
            if wrap_name:
                wrap_config = self._link.config(wrap_name)
                # if its just a string, make a wrapper that is preloaded with
                # the string as the command.   
                if isinstance(wrap_config, str) or isinstance(wrap_config,
                                                              unicode):
                    return Wrapper(__cmd__ = wrap_config)
                
                wrap_config = wrap_config.copy()

            # if they override the config then
            # update what is in the config with the 
            # parameters passed in
            if kwargs:
                wrap_config.update(kwargs)

            # if it is here we want to remove before we pass through
            wrapper = wrap_config.pop('wrapper', None)
                
            # if they tell us what type it should be then use it
            if wrapper:
                try:
                    #look up the module in our wrappers dictionary
                    if not self._link.wrappers:
                        self._link.load_wrappers()
                    wrapper = self._link.wrappers[wrapper]
                except AttributeError as e:
                    raise Exception('Wrapper cannot be found by the' +
                                    ' link class when loading: %s ' % (wrapper))
            else:
                wrapper = Wrapper

            try:
                return wrapper(wrap_name = wrap_name, **wrap_config)
            except TypeError as e:
                raise Exception('Error wrapping configuration with object %s, message %s ' %
                                (wrapper, e.message))

            #otherwise just called the wrapped function
            return self.wrapper_object(**kwargs)

        return get_configured_object

    @linker
    def links(self, wrap = None, **kwargs):
        """
        Returns one or more nosewrapper
        """
        pass

    def __call__(self, wrap_name = None, **kwargs):
        """
        Make it so you can call Linker(wrap) and have that return a link for the
        configured wrap
        """
        return self.links(wrap_name, **kwargs)


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
        return (prev_completions + [c[0] for c in obj_members] + 
                [c for c in obj.config().keys()])

    @complete_object.when_type(Link)
    def complete_link(obj, prev_completions):
        """
        Add in all the methods of the _wrapped object so its
        visible in iPython as well
        """
        return prev_completions + [c for c in obj.config().keys()]

# Importing IPython brings in about 200 modules, so we want to avoid it unless
# we're in IPython (when those modules are loaded anyway).
# Code attributed to Pandas, Thanks Wes 
if "IPython" in sys.modules:  # pragma: no cover
    try:
        install_ipython_completers()
    except Exception:
        pass

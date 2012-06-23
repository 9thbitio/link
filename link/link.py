import os
import sys
import inspect
import json
from utils import load_json_file
from subprocess import Popen

class Commander(object):
    """
    Given a dictionary of commands the commander can run them very easily
    """
    def __init__(self, commands):
        self.commands = commands

    def run_command(self, name = "__default__", **kwargs):
        """
        Run the command in your command dictionary
        """
        if self.commands:
            cmd = self.commands.get(name)
            if cmd:
                p= Popen(cmd,shell=True)
                p.wait()
                return p

        raise(Exception("No such command %s " % name))

       

class Link(object):
    """
    Link is a singleton that keeps all configuration for the program. It is
    used by any Linked object so that there can be a shared configuration across
    the entire program.  The configuration is stored in json in a file called
    .vlink.config
    """
    __link_instance = None
    
    LNK_USER_DIR =  '%s/.link' % os.getenv('HOME')
    LNK_DIR = os.getenv('LNK_DIR') or LNK_USER_DIR
    LNK_CONFIG = LNK_DIR + "/link.config" 
    DEFAULT_CONFIG = {"dbs":{}, "apis":{}}

    @classmethod 
    def plugins_directory(cls):
        """
        Tells you where the external wrapper plugins exist
        """
        if cls.LNK_DIR and os.path.exists(cls.LNK_DIR):
            plugin_dir = cls.LNK_DIR + "/plugins"
            if not os.path.exists(plugin_dir):
                os.makedirs(plugin_dir)
            return plugin_dir
        
        raise Exception("Problem creating plugins, Link directory does not exist")

    @classmethod 
    def plugins_directory_tmp(cls):
        """
        Tells you where the external wrapper plugins exist
        """
        plugins = cls.plugins_directory() 
        tmp = plugins + "/tmp"

        if not os.path.exists(tmp): 
            os.makedirs(tmp)

        return tmp 
        
    @classmethod
    def config_file(cls):
        """
        Gives you the global config based on the hierchial lookup::

            first check $LNK_DIR/link.config
            then check ./link.config

        """

        #if there is a user global then use that 
        if os.path.exists(cls.LNK_CONFIG):
            return cls.LNK_CONFIG
    
        # if they ore in iPython and there is no user config
        # lets create the user config for them 
        if "IPython" in sys.modules:
            if not os.path.exists(cls.LNK_DIR):
                print "Creating user config dir %s " % cls.LNK_DIR
                os.makedirs(cls.LNK_DIR)
            
            print "Creating default user config "
            new_config = open(cls.LNK_CONFIG, 'w')
            new_config.write(json.dumps(cls.DEFAULT_CONFIG)) 
            new_config.close()
            return cls.LNK_CONFIG
        
        raise Exception("""No config found.  Set environment variable LNK_DIR to
                        point to your link configuration directory or create a
                        .link/link.config file in your HOME directory""")

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
        self._commander = self.__config.get('__cmds__')
        self.namespace = namespace
        self.wrappers = {}

    def __init__(self, config_file=None, namespace=None):
        """
        Create a new instance of the Link.  Should be done
        through the instance() method.
        """
        self.wrappers = {}
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

    def __call__(self, wrap_name=None, *kargs, **kwargs):
        """
        Get a wrapper given the name or some arguments
        """
        wrap_config = {}

        if wrap_name:
            wrap_config = self.config(wrap_name)
            # if its just a string, make a wrapper that is preloaded with
            # the string as the command.   
            if isinstance(wrap_config, str) or isinstance(wrap_config, unicode):
                return Wrapper(__cmd__ = wrap_config)

            wrap_config = wrap_config.copy()

        # if they override the config then update what is in the config with the 
        # parameters passed in
        if kwargs:
            wrap_config.update(kwargs)

        # if it is here we want to remove before we pass through
        wrapper = self._get_wrapper(wrap_config.pop('wrapper', None))

        try:
            return wrapper(wrap_name = wrap_name, **wrap_config)
        except TypeError as e:
            raise Exception('Error wrapping configuration with object %s, message %s ' %
                            (wrapper, e.message))

    def _get_wrapper(self, wrapper):
        """
        calls back the function with a fully wrapped class
        """
            
        # if they tell us what type it should be then use it
        if wrapper:
            try:
                #look up the module in our wrappers dictionary
                if not self.wrappers:
                    self.load_wrappers()
                return self.wrappers[wrapper]
            except AttributeError as e:
                raise Exception('Wrapper cannot be found by the' +
                                ' link class when loading: %s ' % (wrapper))
        return Wrapper

    def install_plugin(self, file=None, install_global = False):
        """
        Install the plugin in either their user plugins directory or
        in the global plugins directory depending on what they want to do
        """
        if install_global:
            cp_dir = os.path.dirname(__file__) + '/plugins'
        else:  
            cp_dir = self.plugins_directory()

        import shutil
        print "installing %s into directory %s " % ( file, cp_dir)
        try:
            shutil.copy(file, cp_dir )
        except:
            print "error moving files"

lnk = Link.instance()

class Wrapper(object):
    """
    The wrapper wraps a piece of the configuration.  
    """
    _wrapped = None

    def __init__(self, wrap_name = None, wrapped_object=None, **kwargs):
        self.wrap_name = wrap_name
        self._wrapped = wrapped_object
        self.commander = Commander(kwargs.get("__cmds__"))
        #you want to prefer the wrappers native functions
        #kwargs.update(self.__dict__)
        self.__dict__['__link_config__'] = kwargs
        #self._link = Link.instance()
    
    def __getattr__(self, name):
        """
        wrap a special object if it exists
        """

        #first look for a wrapper item named that
        if name in self.__dict__:
            return self.__getatribute__(name)
        try:
            if self._wrapped is not None:
                return self._wrapped.__getattribute__(name)
        except:
            raise AttributeError("No Such Attribute in wrapper %s" % name)
        
        if self.commander.commands:
            cmd = self.commander.commands.get(name)
            if cmd:
                return self.commander.run_command(name)

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
        #run the command specified by the first param, else run the default
        #cammond
        if kargs and len(kargs)>0:
            command_name = kargs[0]
        else:
            command_name = "__default__"
        
        try:
            return self.commander.run_command(command_name)
        except Exception as e:
            raise e 
            if command_name=="__default__":
                message = "This wrapper is not callable, no default command set"
            else:
                message = "No command set for %s" % command_name
            raise(Exception(message))


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
        if obj._wrapped:
            obj_members = inspect.getmembers(obj._wrapped)
            prev_completions+=[c[0] for c in obj_members]

        prev_completions+=[c for c in obj.config().keys()] 
        prev_completions+=[command for command in obj.commander.commands.keys()]

        return prev_completions

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

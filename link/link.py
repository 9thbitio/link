# -*- coding: utf-8 -*-

"""
link
~~~~~~~~~~~~

The link module helps you connect to all of the data sources you need through a
simple configuration

Sample Config to connect to mysql::

   {
        "dbs":{
           "my_db": {
               "wrapper": "MysqlDB",
               "host": "mysql-master.123fakestreet.net",
               "password": "<password>",
               "user": "<user>",
               "database": "<database_name>"
           }
        }
    }

Sample Code::

    In [3]: from link import lnk

    # uses the keys from your configuration to look up and create the
    # appropriate objects
    In [35]: my_db = lnk.dbs.my_db

    In [36]: data = my_db.select('select id from my_table')

:copyright: (c) 2013 by David Himrod
:license: Apache2, see LICENSE for more details.

"""
from __future__ import print_function
from __future__ import absolute_import

import os
import sys
import inspect
import json
import six

if six.PY3:
    unicode = str
    str = bytes


from subprocess import Popen

from .utils import load_json_file
from .common import Cacheable
from .exceptions import LNKConfigException, LNKAttributeException

# To set up logging manager
from ._logging_setup import LogHandler

# this gets the current directory of link
lnk_dir = os.path.split(os.path.abspath(__file__))[0]

class Callable(object):
    """
    A callable object that has a run_shell method
    """
    @property
    def command(self):
        """
        Here is the command for doing the mysql command
        """
        raise NotImplementedError('You have not defined a command for this Callable Object')

    def __call__(self, command=None, wait=True):
        """
        When you call this Callable it will run the command.  The command can
        either be a string to run on the shell or a function to run in python

        Right now it only supports string commands for the shell
        """
        cmd = command or self.command

        if cmd:
            p = Popen(cmd, shell=True)

            if wait:
                p.wait()
            return p


class Commander(object):
    """
    Given a dictionary of commands the commander can run them very easily
    """
    def __init__(self, commands=None, base_dir=''):

        self.base_dir = base_dir
        self.commands = {}

        if commands:
            self.commands = commands
        elif not commands and self.base_dir:
            self.commands = dict([(key, key) for key in self.list_base_dir()])
        else:
            self.commands = {}

    def set_base_dir(self, base_dir):
        """
        set the base dir which will uncache the commands it has stored
        """
        self.base_dir = base_dir

    def list_base_dir(self):
        """
        list what is in the base_dir, nothing if doesnt exist
        """
        try:
            return os.listdir(self.base_dir)
        except:
            return []

    def has_command(self, name):
        """
        Returns true if this commander has a command by this name
        """
        return name in self.commands

    def run_command(self, name="__default__", base_dir='', *kargs, **kwargs):
        """
        Run the command in your command dictionary
        """
        if not base_dir:
            base_dir = self.base_dir

        if self.commands:
            # make a copy of the arra
            cmd = self.commands.get(name)
            if cmd:
                if not isinstance(cmd, list):
                    cmd = [cmd]
                # make a copy of it so you don't change it
                else:
                    cmd = cmd[:]

                cmd.extend(map(str, kargs))
                cmd = '%s/%s' % (base_dir, "/".join(cmd))
                p = Popen(cmd, shell=True)
                p.wait()
                return p

        raise Exception

    def command(self, name=None):
        """
        Returns the command function that you can pass arguments into
        """
        def runner(*kargs, **kwargs):
            return self.run_command(name, *kargs, **kwargs)

        return runner


class Link(object):
    """
    Link is a singleton that keeps all configuration for the program. It is
    used by any Linked object so that there can be a shared configuration across
    the entire program.  The configuration is stored in json in a file called
    .vlink.config
    """
    __link_instance = None
    __msg = None
    __name__ = "lnk"

    LNK_USER_DIR = '%s/.link' % os.getenv('HOME')
    LNK_DIR = os.getenv('LNK_DIR') or LNK_USER_DIR
    LNK_CONFIG = LNK_DIR + "/link.config"
    DEFAULT_CONFIG = {"dbs": {}, "apis": {}}

    def __init__(self, config_file=None, namespace=None):
        """
        Create a new instance of the Link.  Should be done
        through the instance() method.
        """
        # this will be lazy loaded
        self.__config = None
        self.wrappers = {}
        self.fresh(config_file, namespace)

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

        # if there is a user global then use that
        if os.path.exists(cls.LNK_CONFIG):
            return cls.LNK_CONFIG

        # if they ore in iPython and there is no user config
        # lets create the user config for them
        if "IPython" in sys.modules:
            if not os.path.exists(cls.LNK_DIR):
                print("Creating user config dir %s " % cls.LNK_DIR)
                os.makedirs(cls.LNK_DIR)

            print("Creating default user config ")
            new_config = open(cls.LNK_CONFIG, 'w')
            new_config.write(json.dumps(cls.DEFAULT_CONFIG))
            new_config.close()
            return cls.LNK_CONFIG

        return None

    def _get_all_wrappers(self, mod_or_package):
        """
        Given a module or package name in returns all
        classes that could possibly be a wrapper in
        a dictionary
        """
        try:
            wrapper_mod = __import__(mod_or_package, fromlist=['*'])
        except ImportError as e:
            raise

        # get all classes by name and put them into a dictionary
        wrapper_classes = dict([(name, cls) for name, cls in
                                inspect.getmembers(wrapper_mod) if
                                inspect.isclass(cls)])
        return wrapper_classes

    def load_wrappers(self):
        """
        loads up all the wrappers that can be accessed right now
        """
        # load all the standard ones first
        self.wrappers = self._get_all_wrappers('link.wrappers')
        directories = self._config.get('external_wrapper_directories')
        self.load_wrapper_directories(directories)
        packages = self._config.get('external_wrapper_packages')
        self.load_wrapper_packages(packages)

    def load_wrapper_directories(self, directories):
        """
        Load in all of the external_wrapper_directories
        """
        if directories:
            for ext_path in directories:
                path_details = ext_path.rstrip('/').split('/')
                # the path we add to sys.path is this without the last word
                path = '/'.join(path_details[:-1])
                mod = path_details[-1]
                # TODO: Need to put an error here if this directory does not
                # exist
                if path not in sys.path:
                    sys.path.append(path)
                wrapper_classes = self._get_all_wrappers(mod)
                self.wrappers.update(wrapper_classes)

    def load_wrapper_packages(self, packages):
        """
        load in all of the external_wrapper_packages
        """
        # load in all the packages
        if packages:
            for ext_mod in packages:
                wrapper_classes = self._get_all_wrappers(ext_mod)
                self.wrappers.update(wrapper_classes)

    @property
    def _config(self):
        """
        Lazy load the config so that any errors happen then
        """
        if not self.__config_file:
            # If there is not config file then return an error.
            # TODO: Refactor the config code, it's overly confusing
            raise Exception("""No config found.  Set environment variable LNK_DIR to
                        point to your link configuration directory or create a
                        #.link/link.config file in your HOME directory""")

        if not self.__config:
            try: 
                self.__config = load_json_file(self.__config_file)
            except:
                raise LNKConfigException("Error parsing config")

        return self.__config

    def fresh(self, config_file=None, namespace=None):
        """
        sets the environment with a fresh config or namespace that is not
        the defaults if config_file or namespace parameters are given
        """
        if not config_file:
            config_file = self.config_file()

        self.__config_file = config_file
        self.__config = None
        # I don't think i want to support this feature anymore
        # self._commander = self.__config.get('__cmds__')
        # self._commander = self.__config.get('__scripts__')
        self.namespace = namespace
        self.wrappers = {}

    def configure_msg(self, overrides={}, keep_existing=True, verbose=False):
        """
        Optional method to supplement or override logging configuration from a passed-in
        dictionary; OR to turn on verbose logging. If this method is not invoked,
        logging will be set up with any logging configurations found in the link config.
        This method is useful if you want to define job- or application-specific logging
        setups, so that you do not have to keep changing link.config.

        NOTE: if this is called after lnk.msg has been used, it will create a new
        LogHandler that will override the existing one.

        :param dict overrides: dictionary of logging options
        :param bool keep_existing: whether to supplement (True) or completely override
            (False) any existing logging (i.e. link.config options).
        """
        if not keep_existing:
            log_conf = overrides
        else:
            log_conf = self._config.get('msg', {})
            log_conf.update(overrides)

        self.__msg = LogHandler(log_conf, verbose)
        return self.__msg

    # The fact that Link is a singleton should ensure that only one instance of
    # LogHandler will be created (if Link is used correctly...)
    @property
    def msg(self, verbose=False):
        """
        Get (and create if doesn't already have) the LoggingHandler for link

        :param bool verbose: log to stdout (DEBUG and higher) in addition to any other
            logging setup
        """
        if not self.__msg:
            self.__msg = LogHandler(self._config.get('msg', {}), verbose)
        return self.__msg

    def __getattr__(self, name):
        """
        The lnk object will first look for its native functions to call.
        If they aren't there then it will create a wrapper for the configuration
        that is led to by "name"
        """
        try:
            return self.__getattribute__(name)
        except Exception as e:
            return self(wrap_name=name, **self.config(name).copy())

    def config(self, config_lookup=None):
        """
        If you have a conf_key then return the
        dictionary of the configuration
        """
        ret = self._config

        if config_lookup:
            try:
                for value in config_lookup.split('.'):
                    ret = ret[value]
            except KeyError:
                raise LNKAttributeException('No such configured object %s' % config_lookup)
            return ret

        return ret

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
                return Wrapper(__cmd__=wrap_config)

            wrap_config = wrap_config.copy()

        # if they override the config then update what is in the config with the
        # parameters passed in
        if kwargs:
            wrap_config.update(kwargs)

        # if it is here we want to remove before we pass through
        wrapper = self._get_wrapper(wrap_config.pop('wrapper', None))
        return wrapper(wrap_name=wrap_name, **wrap_config)

    def _get_wrapper(self, wrapper):
        """
        calls back the function with a fully wrapped class
        """

        # if they tell us what type it should be then use it
        if wrapper:
            try:
                # look up the module in our wrappers dictionary
                if not self.wrappers:
                    self.load_wrappers()
                return self.wrappers[wrapper]
            except AttributeError as e:
                raise Exception('Wrapper cannot be found by the' +
                                ' link class when loading: %s ' % (wrapper))
        return Wrapper

    def install_plugin(self, file=None, install_global=False):
        """
        Install the plugin in either their user plugins directory or
        in the global plugins directory depending on what they want to do
        """
        if install_global:
            cp_dir = os.path.dirname(__file__) + '/plugins'
        else:
            cp_dir = self.plugins_directory()

        import shutil
        print("installing %s into directory %s " % (file, cp_dir))
        try:
            shutil.copy(file, cp_dir)
        except:
            print("error moving files")


lnk = Link.instance()


class Wrapper(Callable):
    """
    The wrapper wraps a piece of the configuration.
    """
    _wrapped = None
    cmdr = None

    def __init__(self, wrap_name=None, wrapped_object=None, **kwargs):
        super(Wrapper, self).__init__()
        self.wrap_name = wrap_name
        self._wrapped = wrapped_object

        self.commander = Commander(kwargs.get("__cmds__"))
        self.lnk_script_commander = Commander(base_dir =
                                         '%s/scripts' % lnk_dir)
        self.script_commander = Commander(base_dir =
                                         '%s/scripts' % os.getcwd())
        self.cmdr = self.script_commander
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
            return lnk(wrapper)

        raise AttributeError("No such attribute found %s" % name)
    
    def __getitem__(self, name):
        return self.__getattr__(name)

    def config(self):
        return self.__link_config__


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
            prev_completions += [c[0] for c in obj_members]

        prev_completions += [c for c in obj.config().keys()]
        prev_completions += [command for command in obj.commander.commands.keys()]
        prev_completions += [command for command in obj.script_commander.commands.keys()]
        prev_completions += [command for command in obj.lnk_script_commander.commands.keys()]

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

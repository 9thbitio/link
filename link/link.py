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

import inspect
import json 

from . import __GET_LINK__
from ._utils import load_json_file, deprecated
from ._common import Cacheable

from wrappers import Wrapper as _Wrapper

# To set up logging manager
from _logging_setup import LogHandler as _LogHandler

class Link(object):
    """
    Link is a singleton that keeps all configuration for the program. It is
    used by any Linked object so that there can be a shared configuration across
    the entire program.  The configuration is stored in json in a file called
    .vlink.config
    """
    __link_instance = None
    __msg = None

    DEFAULT_CONFIG = {"dbs": {}, "apis": {}}

    def __init__(self, config_file=None):
        """
        Create a new instance of the Link.  Should be done
        through the instance() method.
        """
        # this will be lazy loaded
        self._config = None
        self.wrappers = {}
        self.refresh(config_file)

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

    def _reset_config(self):
        """
        Lazy load the config so that any errors happen then
        """
        if not self._config_file:
            # If there is not config file then return an error.
            # TODO: Refactor the config code, it's overly confusing
            raise Exception("""No config found.  Set environment variable LNK_DIR to
                        point to your link configuration directory or create a
                        #.link/link.config file in your HOME directory""")

        self._config = load_json_file(self._config_file)

    def refresh(self, config_file=None):
        """
        sets the environment with a fresh config or namespace that is not
        the defaults if config_file or namespace parameters are given
        """

        #if they don't pass in a config file just get the normal_one
        if config_file:
            self._config_file = config_file 

        #by setting this to none you are clearing_config
        self._reset_config()

        # I don't think i want to support this feature anymore
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

        self.__msg = _LogHandler(log_conf, verbose)
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
            self.__msg = _LogHandler(self._config.get('msg', {}), verbose)
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
            return self.get_link(link_name=name, **self._config[name].copy())

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
                raise KeyError('No such configured object %s' % config_lookup)
            return ret

        return ret
    
    @deprecated
    def __call__(self, wrap_name=None, *kargs, **kwargs):
        """
        Deprecated, please use get_link
        """
        return self.get_link(wrap_name, *kargs, **kwargs)

    def get_link(self, link_name=None, *kargs, **kwargs):
        """
        Get a configured link object by it's name 
        """
        wrap_config = {}
        
        print "link name {} ".format(link_name)
        if link_name:
            wrap_config = self.config(link_name)
            # if its just a string, make a wrapper that is preloaded with
            # the string as the command.
            if isinstance(wrap_config, str) or isinstance(wrap_config, unicode):
                return _Wrapper(__cmd__=wrap_config)

            wrap_config = wrap_config.copy()

        # if they override the config then update what is in the config with the
        # parameters passed in
        if kwargs:
            wrap_config.update(kwargs)

        # if it is here we want to remove before we pass through
        wrapper = self._get_wrapper(wrap_config.pop('wrapper', None))

        wrap_config.pop('wrap_name', None)

        return wrapper(wrap_name=link_name, **wrap_config)

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
        return _Wrapper


def install_ipython_completers():  # pragma: no cover
    """Register the Panel type with IPython's tab completion machinery, so
    that it knows about accessing column names as attributes."""
    from IPython.utils.generics import complete_object
    import inspect

    @complete_object.when_type(_Wrapper)
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



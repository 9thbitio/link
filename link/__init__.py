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
#import all of this version information
__version__ = '1.0.0'
__author__ = 'David Himrod'
__license__ = 'Apache 2.0'
__copyright__ = 'Copyright 2013 David Himrod'
__title__ = 'link'

import os
import sys

__DEFAULT_CONFIG__ = {"dbs":{}, "apis":{}}

def create_config(location, config_data=None, force=False):
    # if they ore in iPython and there is no user config
    # lets create the user config for them
    if os.path.exists(location) and not force:
        return False
    
    if not config_data: 
        config_data = __DEFAULT_CONFIG__

    new_config = open(location, 'w')
    new_config.write(json.dumps(config_data))
    new_config.close()
    return True



#must go before the import of Link
def __GET_LINK__(link_name):
    return lnk.get_link(link_name)
 
from link import Link, install_ipython_completers

LNK_USER_DIR = '%s/.link' % os.getenv('HOME')

# You can override the default location with the environment variable LNK_DIR
LNK_DIR = os.getenv('LNK_DIR') or LNK_USER_DIR

LNK_CONFIG = LNK_DIR + "/link.config"

lnk = Link(LNK_CONFIG)

   
if "IPython" in sys.modules:
    #create the config
    if not os.path.exists(LNK_CONFIG):
        print "Creating default user config "
        create_config(LNK_CONFIG)
    
    #install the tab completers
    try:
        install_ipython_completers()
    except Exception:
        pass

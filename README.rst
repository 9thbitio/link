===================
Link - Beta 
===================

NOT a new technology, but helps link together many well established (opensource)
technologies like Requests, Pandas, MysqlDB and Sqlite3...to begin with

Goals:
    
    * Create an easy and simple development environment and process
    * Make configuration easy for complex environments
        * and dynamic object creation
    * Allow people wrap their own apis, dbs, and other pieces of the system and plug them into link

Background:
^^^^^^^^^^^^

    Link was created to meet the needs of many different types of people.  
    Link was originally created to make configuration easy, generic and standardized.  

Installation:
^^^^^^^^^^^^^^

The latest stable can be installed using easy_install or pip::

    sudo pip install link

or::

    sudo easy_install install link

You can also clone and install it::

    git clone git@github.com:dhrod5/link.git 
    cd link
    python setup.py install

Configuration:
^^^^^^^^^^^^^^^

Your configuration drives the usage of link.  Everything that is in your
configuration can be treated like an object.  Here is an example config::

    {
        "apis": {
           "my_api": {
               "wrapper": "APIRequestWrapper",
               "base_url": "http://123fakestreet.net",
               "user": "<user>",
               "password": "<password>"
           },
           "my_api_2": {
               "wrapper": "APIRequestWrapper",
               "base_url": "http://123fakestreet.net",
               "user": "<user>",
               "password": "<password>"
           },
        },
        "dbs":{
           "my_db1": {
               "wrapper": "MysqlDBConnectionWrapper",
               "host": "mysql-master.123fakestreet.net",
               "password": "<password>",
               "user": "<user>",
               "database": "<database_name>"
           }
        }
    } 


Using Link
^^^^^^^^^^^^

You can get one of these objects by calling on lnk.  lnk is a singleton that
wraps your configuration to auto generate objects::

        In [4]: lnk("apis.my_api")
        Out[4]: <apiwrappers.APIRequestWrapper at 0x105266e10>

In addition, you can treat everything in your config as if it is an object.
Under the hood it is calling the same thing as lnk("apis.my_api").  Note that
every time you call this it makes a NEW APIRequestWrapper, so set it to a
variable::

        In [4]: lnk.apis.my_api
        Out[4]: <apiwrappers.APIRequestWrapper at 0x10526f390>

iPython integration:
^^^^^^^^^^^^^^^^^^^^^^

One of the nice features of link is that you can tab complete into your
config.  For instance::

    In [1]: from link import lnk

    In [2]: lnk.<hit tab>
    lnk.dbs                        lnk.apis
    lnk.config                     lnk.fresh

    In [2]: lnk.dbs.<hit tab>
    lnk.dbs.config           lnk.my_db1

Even though these are not objects yet, ipython knows what objects are available
and will show them in your completion.  

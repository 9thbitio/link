===================
Link - Beta 
===================

Link was designed to deal with the growing number of databases, apis and
environments needed to grow a technology and a team.  Link provides a simple way
to configure and connect to all of these different technologies.  

Goals:
    
    * Create an easy and simple development environment and process
    * Make configuration easy for complex environments
    * Allow people wrap their own apis, dbs, and other pieces of the system and plug them into link

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

Requirements:
^^^^^^^^^^^^^^

I've attempted to make it so that no packages are required to actually install
link.  However, most of the wrappers that are available depend on other
opensource packages to work.  For example, to connect to a mysql database you
will be using the MysqlDB wrapper, which requires that you have MySqldb
installed.  Here is a list of packages that may be used.::

    mysql-python ==> MysqlDB
    requests ==> Any APIWrapper
    happybase ==> HbaseDB
    pymongo ==> MongoDB
    pyscopg ==> PostgresDB

You should be able to pip or easy_install any of these packages very easily

Using Link:
^^^^^^^^^^^^

If you are like me, you are dealing with a lot of different technologies in your
environment.  Some are accessed by api, some are database connections, others
need special configuration and logic to use.  Link lets you "wrap" each piece
and centralize the configuration of these pieces.  Then, all of these pieces can
be accessed in a standardized way, with a tight integration with ipython 

Configuration:
^^^^^^^^^^^^^^^

Your configuration drives the usage of link.  You need to create your
configuration in your home directory (~/.link/link.config)::

    mkdir ~/.link
    vi ~/.link/link.config

Everything that is in your configuration can be treated like an object which
will be explained later.  For now, Here is an example JSON config::

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
           "my_db": {
               "wrapper": "MysqlDB",
               "host": "mysql-master.123fakestreet.net",
               "password": "<password>",
               "user": "<user>",
               "database": "<database_name>"
           }
        }
    } 

You can organize your configuration anyway you would like, using any names you
wish.  For example, you could create an environment centric structure like this::

    {
     "prod": { "my_api":..., "my_db":...},
     "sand": { "my_api":..., "my_db":...}
     }

You can also nest resources as deep as you would like::

    {
     "prod": { 
        "dbs":{
            "my_db":...
        },
        "apis":{
            "my_api":...
        }
      },
    "sand": { 
        "dbs":{
            "my_db":...
        },
        "apis":{
            "my_api":...
        }
      }
     }

The only rule is that names cannot have a "." in them, you will see why below.
Create a structure that fits your usecase, by environment, by client (if you are
a consultant)...etc.

Wrappers
^^^^^^^^^

You probably noticed the fact that every resource has a wrapper.  The wrapper
tells link what type of object this resource is.  When link creates these
resources it will create the object and pass it the parameters you have
configured.  The wrappers that ship with link are::
    
    APIRequestWrapper
    MysqlDB
    SqliteDB
    HbaseDB
    MongoDB

Note, these have dependancy package requirements for them to work

The lnk Singleton
^^^^^^^^^^^^^^^^^^^

When you get started you want to import lnk, which is a singleton that contains
all of the configuration details from ~/.link/link.config::

    In [4]: from link import lnk

**NOTE:**: If your config file is not proper json you will get an error when
trying to import lnk

You can look at what is in your configuration using the config() function, which will return a
dictionary.
    
        In [3]: lnk.config().keys()
        Out[3]: ['dbs', 'apis']

Accessing Configured Resources
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The lnk object let's you treat everything in your configuration as an object.
For instance, let's say we have this as our configuration::

    {
        "apis": {
           "my_api": {
               "wrapper": "APIRequestWrapper",
               "base_url": "http://123fakestreet.net",
               "user": "<user>",
               "password": "<password>"
           }
    }
 
I can access my_api by calling lnk.apis.my_api.  This may seem strange, but lnk
under the hood will cascade through the configuration and create objects::
    
        In [3]: from link import lnk

        # Save my_api to the api variable to avoid creating many copies
        In [4]: api = lnk.apis.my_api

        In [5]: api 
        Out[5]: <apiwrappers.APIRequestWrapper at 0x10526f390>

**Note**: every time you do **this it makes a NEW APIRequestWrapper**, so set it to a
variable.  You will see below in the iPython integration why this is so powerful::


API Responses to Json and XML:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The APIResponseWrapper has convience functions for json and xml responses::

        In [3]: from link import lnk

        # Save my_api to the api variable to avoid creating many copies
        In [4]: api = lnk.apis.my_api

        In [9]: resp = api.get('/api_service?param=blah')

        # look at the raw content
        In [10]: resp
        Out[10]: '{"total":0,"rank":"0","success":true}'

        # json deserialize into a dictionary using the json property
        In [11]: resp.json['success']
        Out[11]: true 

        In [12]: resp.json['total']
        Out[12]: 0

        In [43]: type(resp.json)
        Out[43]: dict

For xml there is an xml property.  It will return the results as pythons xml.etree.cElementTree.

DBConnections
^^^^^^^^^^^^^^^

Database connections work the same way::

    In [3]: from link import lnk

    In [35]: my_db = lnk.dbs.my_db

    In [36]: data = my_db.select('select id from my_table')
    
    #returns a cursor wrapper which has some conviennce funtions
    In [10]: data
    Out[10]: <link.wrappers.dbwrappers.DBCursorWrapper at 0x10b318a50>

        In [12]: [x for x in data]
        Out[12]: 
        [(6L,),
        (4L,),
        (9L,),
        (8L,),
        (7L,),
        (3L,),
        (2L,),
        (1L,),
        (12L,),
        (13L,),
        (5L,),
        (10L,),
        (11L,),
        (14L,)]


Queries to Pandas Dataframes
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you don't know about pandas you are missing out (make sure its installed).  
You can select any query into Pandas DataFrames using the select function
instead of the select function of a DBConnectionWrapper::

    In [35]: my_db = lnk.dbs.my_db

    In [36]: df = my_db.select('select * from my_table').as_dataframe()

pandas allows you to do groupbys, sums, aggregations, joins...and much more in
memory.  For more information see the pandas homepage (TODO put link in here)

iPython Integration - Tab Completion:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Object Tab Completion**

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

**Wrapped Function Tab completion**

This feature is a little strange at first.  all Wrappers have a _wrapped object.
The _wrapped object is what it is "wrapping".  In the case of an
APIRequestWrapper, we are wrapping the Requests Session object::

        In [15]: api._wrapped
        Out[15]: <requests-client at 0x101509a90>

Requests is an extremely flexible package for interacting with apis, and making
http requests.  So, I wanted to make sure that I was not taking away from the
functionality of this package.  Rather, making it easy to use this package by
injecting in your configuration (like username, password and custom auth).
Another fancy iPython trick is when you tab complete you object, you will see
all the available functions and properties of the _wrapped object.::

        In [16]: api.<hit tab>
        api.apikey            api.cert              api.delete            api.hooks
        api.password          api.prefetch          api.requests          api.timeout
        api.auth              api.clear_session     api.get
        api.init_poolmanager  api.patch             api.proxies
        api.response_wrapper  api.user
        api.authenticate      api.config            api.head              api.options
        api.poolmanager       api.put               api.run_command       api.verify
        api.base_url          api.cookies           api.headers           api.params
        api.post              api.request           api.secret            api.wrap_name
    
        # this is a method of the _wrapped requests Session object
        # but seems as though it belongs to api in tab completion and when you
        # call it
        In [19]: api.delete
        Out[19]: <bound method Session.delete of <requests-client at 0x101509a90>>

Note, if your wrapper and the _wrapped object have the same function, your
function will override the _wrapped function.

iPython Integration - Lazy Environments 
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

I like using iPython while I am developing, sometimes when I am not even
developing in python.  If you noticed, my configuration includes all the
resources I use all the time.  Yet, I am using aliases to use the commandline
tools for things like mysql, sqlite,
postgres...curl...vertica...netezza...  Really, almost anything you can wrap.
It would be nice if i could somehow use what I have configured in ipython to use
the command-line tool.  Just call your Wrapper like a function::

        In [22]: my_db = lnk.dbs.my_sqlitedb

        In [23]: my_db()
        SQLite version 3.7.7 2011-06-25 16:35:41
        Enter ".help" for instructions
        Enter SQL statements terminated with a ";"
        sqlite>

        sqlite> .exit

        In [24]:

Same with mysql::

        In [24]: my_db = lnk.dbs.my_mysql

        In [25]: my_db()
        Welcome to the MySQL monitor.  Commands end with ; or \g.
        Your MySQL connection id is 1876
        Server version: 5.5.24 MySQL Community Server (GPL)

        Copyright (c) 2000, 2011, Oracle and/or its affiliates. All rights reserved.

        Oracle is a registered trademark of Oracle Corporation and/or its
        affiliates. Other names may be trademarks of their respective
        owners.

        Type 'help;' or '\h' for help. Type '\c' to clear the current input statement.

        mysql> show tables....

        mysql> exit

        In [26]: 

When you exit you are right back in your ipython session, like nothing happened
at all. 


================
SUPER BETA
================

Create Lazy Commands:
^^^^^^^^^^^^^^^^^^^^^^

You can easily attach "lazy" commands to anything that you config.  These
commands will not run if they have the same name of a function in the class
itself.  

We will use hbase and hadoop as an example.  I haven't written a wrapper for
these yet, but i want to be able to manage the start up and shutdown of the
hadoop and hbase servers without having to remember the command, or having to
leave my IPython session.  You can add the following to your configuration::

        "hbase":{
            "__cmds__":{
                "start":["$HBASE_HOME/bin/start-hbase.sh"],
                "stop":["$HBASE_HOME/bin/stop-hbase.sh"]
            }
        },
        "hadoop":{
            "__cmds__":{
                "start":["$HADOOP_HOME/bin/start-all.sh"],
                "stop":["$HADOOP_HOME/bin/stop-all.sh"]
            }
        }

In the IPython I can easily start and stop hadoop and hbase::

    In [9]: hbase = lnk.dbs.hbase

    In [3]: hbase.<hit tab>
    hbase.commander    hbase.config       hbase.run_command  hbase.start
    hbase.stop         hbase.wrap_name
    
    #start it up
    In [4]: hbase.start 
    home.lei.local: ssh: Could not resolve hostname home.lei.local: nodename nor
    servname provided, or not known
    starting master, logging to
    /var/hbase/logs/hbase-master.local.out
    nohup: can't detach from console: Inappropriate ioctl for device
    localhost: starting regionserver, logging to
    /var/hbase/bin/../logs/hbase-regionserver.local.out
    


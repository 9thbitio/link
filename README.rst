===================
Link - Beta 
===================

Link is NOT a new technology, but helps link together many well established (opensource)
technologies like Requests, Pandas, MysqlDB and Sqlite3...to begin with

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

Depends on what wrappers you are trying to use.  At the very least you need
requests if you are using the apiwrappers.  In addition, these packages are
used::

    MySqldb
    numpy
    pandas


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
               "wrapper": "MysqlDBConnectionWrapper",
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
    MysqlDBConnectionWrapper
    SqliteDBConnectionWrapper

Note, these have dependancy package requirements for them to work

Accessing Configured Resources
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You can get one of these objects by calling on lnk.  lnk is a singleton that
wraps your configuration to auto generate objects::

        In [4]: api = lnk("apis.my_api")

        In [5]: api 
        Out[5]: <apiwrappers.APIRequestWrapper at 0x105266e10>

        In [9]: api.get('/api_service?param=blah').content  
        Out[9]: '{"total":0,"rank":"0","success":true}'

In addition, you can treat everything in your config as if it is an object.
Under the hood it is calling the same thing as lnk("apis.my_api").  Note that
every time you **call this it makes a NEW APIRequestWrapper**, so set it to a
variable.  You will see below in the iPython integration why this is so powerful::
    
        # Save my_api to the api variable to avoid creating many copies
        In [4]: api = lnk.apis.my_api

        In [5]: api 
        Out[5]: <apiwrappers.APIRequestWrapper at 0x10526f390>

API Responses to Json and XML:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The APIResponseWrapper has convience functions for json and xml responses::

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

Queries to Pandas Dataframes
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you don't know about pandas you are missing out (make sure its installed).  
You can select any query into Pandas DataFrames using the select_dataframe function
instead of the select function of a DBConnectionWrapper::

    In [35]: my_db = lnk.dbs.my_db

    In [36]: df = my_db.select_dataframe('select * from my_table')

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

Create your Own Links with Custom Wrappers
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Ideally, I will be able to wrap as many commonly used technologies as possible.
However, I want to open up link for others to write their own wrappers.  I saw a
really interesting wrapper that overrides the APIRequestWrapper to make calls to
graphite, and turns rawData=true calls into DataFrames. 

Today, plugging in your own wrappers is possible, but it is clunky.  I am working on
making this an easier process, and creating a community of powerful links to the
resources we need. 

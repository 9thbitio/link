Using with iPython 
=========================================

Link has been designed to work with iPython to make development and data
exploration easier.

Tab Completion
-----------------

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

Lazy Environments 
--------------------

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




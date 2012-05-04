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

iPython integration:
^^^^^^^^^^^^^^^^^^^^^^

    

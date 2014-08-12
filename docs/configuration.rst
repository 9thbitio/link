Configuration:
=================

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



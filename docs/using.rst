Using Link:
============

If you are like me, you are dealing with a lot of different technologies in your
environment.  Some are accessed by api, some are database connections, others
need special configuration and logic to use.  Link lets you "wrap" each piece
and centralize the configuration of these pieces.  Then, all of these pieces can
be accessed in a standardized way, with a tight integration with ipython 

Wrappers
----------

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
--------------------

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
---------------------------------

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
-------------------------------

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
---------------

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
-----------------------------

``pandas`` users: you can select any query into Pandas DataFrames using the
select function instead of the select function of a DBConnectionWrapper::

    In [35]: my_db = lnk.dbs.my_db

    In [36]: df = my_db.select('select * from my_table').as_dataframe()

    <class 'pandas.core.frame.DataFrame'>
    Int64Index: 325 entries, 0 to 324
    Data columns:
    id               325  non-null values
    user_id          323  non-null values
    app_id           325  non-null values
    name             325  non-null values
    body             325  non-null values
    created          324  non-null values
    dtypes: float64(2), int64(3), object(4)

pandas allows you to do groupbys, sums, aggregations, joins...and much more in
memory.  For more information see the
`pandas homepage <https://pandas.pydata.org/>`__.



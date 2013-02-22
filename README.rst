
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

Here is an example of grabbing data from a database and turning it into an
dataframe::

    In [1]: from link import lnk

    In [2]: my_db = lnk.dbs.my_db

    In [3]: df = my_db.select('select * from my_table').as_dataframe()

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


Docs:
^^^^^^^^^

For information on installing, setting up and using link, check out our `docs <https://link-docs.readthedocs.org/en/latest/>`_ 



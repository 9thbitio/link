.. Link documentation master file, created by
   sphinx-quickstart on Sun Jan 27 16:23:24 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.


Link: Consistent access to the data you care about
====================================================

link Release v\ |version|. (:ref:`Installation <install>`)

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



Contents:

.. toctree::
   :maxdepth: 2
    
   install
   configuration
   using
   ipython


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


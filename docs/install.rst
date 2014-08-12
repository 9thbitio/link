

Installation:
==============

The latest stable can be installed using easy_install or pip::

    sudo pip install link

or::

    sudo easy_install link

You can also clone and install it::

    git clone git@github.com:dhrod5/link.git 
    cd link
    python setup.py install

Requirements:
---------------

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




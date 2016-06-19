from . import Wrapper
from link._utils import list_to_dataframe, deprecated
from contextlib import closing
import defaults

MYSQL_CONNECTION_ERRORS = (2006, 2013)

class DBCursorWrapper(Wrapper):
    """
    Wraps a select and makes it easier to tranform the data
    """
    def __init__(self, cursor, query = None, wrap_name = None, args=None):
        self.cursor = cursor
        self._data = None
        self._columns = None
        self.query = query
        self.args = args or ()
        super(DBCursorWrapper, self).__init__(wrap_name, cursor)

    @property
    def columns(self):
        if not self._columns:
            self._columns = [x[0].lower() for x in self.cursor.description]
        return self._columns

    @property
    def data(self):
        if not self._data:
            with closing(self.cursor) as cursor:
                self._data = cursor.fetchall()
                # since we want to close cursor after we pull the data...
                self._columns = [x[0].lower() for x in self.cursor.description]
        return self._data

    def as_dataframe(self):
        try:
            from pandas import DataFrame
        except:
            raise Exception("pandas required to select dataframe. Please install"  +
                            "sudo easy_install pandas")
        #check to see if they have duplicate column names
        columns = self.columns

        if len(columns)>len(set(columns)):
            raise Exception("Cannot have duplicate column names "
                            "in your query %s, please rename" % columns)
        return list_to_dataframe(self.data, columns)

    def _create_dict(self, row):
        return dict(zip(self.columns, row))

    def as_dict(self):
        return map(self._create_dict,self.data)

    def __iter__(self):
        return self.data.__iter__()

    def execute(self):
        """
        Creates a cursor and executes the query for you
        """
        self.args
        self.query

        #sqlite db does not take in args...so i have to do this
        #TODO: Create custom dbcursor wrappers for different database types
        if self.args:
            self.cursor.execute(self.query, args=self.args)
        else:
            self.cursor.execute(self.query)

        return self


class DBConnectionWrapper(Wrapper):
    """
    wraps a database connection and extends the functionality
    to do tasks like put queries into dataframes
    """
    CURSOR_WRAPPER = DBCursorWrapper

    def __init__(self, wrap_name = None, **kwargs):

        if kwargs:
            self.__dict__.update(kwargs)

        #get the connection and pass it to wrapper os the wrapped object
        connection = self.create_connection()
        super(DBConnectionWrapper, self).__init__(wrap_name, connection)

    def execute(self, query, args = ()):
        """
        Creates a cursor and executes the query for you
        """
        cursor = self._wrapped.cursor()
        return self.CURSOR_WRAPPER(cursor, query, args=args).execute()

    @deprecated("please use select(query).as_dataframe()")
    def select_dataframe(self, query, args=()):
        """
        Select everything into a datafrome with the column names
        being the names of the colums in the dataframe
        """
        try:
            from pandas import DataFrame
        except:
            raise Exception("pandas required to select dataframe. Please install"  +
                            "sudo easy_install pandas")

        cursor = self.execute(query, args = args)
        return cursor.as_dataframe()

    def select(self, query=None, args=()):
        """
        Run a select and just return everything. If you have pandas installed it
        is better to use select_dataframe if you want to do data manipulation
        on the results
        """
        return self.execute(query, args = args)

    def create_connection(self):
        """
        Override this function to create a depending on the type
        of database

        :returns: connection to the database you want to use
        """
        pass

    def use(self, database):
        """
        Switch to using a specific database
        """
        pass

    def databases(self):
        """
        Returns the databases that are available
        """
        pass

    def tables(self):
        """
        Returns the tables that are available
        """
        pass

    def now(self, offset=None):
        """
        Returns the time now according to the database.  You can also pass in an
        offset so that you can add or subtract hours from the current
        """
        try:
            return self.select('select now()').data[0][0]
        except:
            raise Exception("the default select now() does not work on this database"
                            + " override this function if you would like this "
                            + "feature for your database ")
    @property
    def command(self):
        """
        Here is the command for doing the mysql command
        """
        raise NotImplementedError('no shell command for using this database')


class SqliteDB(DBConnectionWrapper):
    """
    A connection wrapper for a sqlite database
    """
    def __init__(self, wrap_name=None, path=None, create_db = True):
        """
        A connection for a SqlLiteDb.  Requires that sqlite3 is
        installed into python

        :param path: Path to the sqllite db.
        :param create_db: if True Create if it does not exist in the
                          file system.  Otherwise throw an error
        """
        self.create_db = create_db

        if not path:
            raise Exception("Path Required to create a sqllite connection")
        super(SqliteDBConnectionWrapper, self).__init__(wrap_name=wrap_name,
                                                  path=path)

    def create_connection(self):
        """
        Override the create_connection from the DbConnectionWrapper
        class which get's called in it's initializer
        """
        return self._connection_from_path(self.path)

    def _connection_from_path(self, path):
        import sqlite3
        db = sqlite3.connect(path)
        return db

    def __call__(self):
        """
        Run's the command line sqlite application
        """
        self.run_command('sqlite3 %s' % self.path)


SqliteDBConnectionWrapper = SqliteDB

class NetezzaDB(DBConnectionWrapper):

    def __init__(self, wrap_name=None, user=None, password=None,
                 host=None, database=None):
        self.user = user
        self.password = password
        self.host = host
        self.database = database
        super(NetezzaDB, self).__init__(wrap_name=wrap_name)

    def create_connection(self):
        """
        Override the create_connection from the Netezza
        class which get's called in it's initializer
        """
        import pyodbc
        connection_str="DRIVER={%s};SERVER=%s;DATABASE=%s;UID=%s;PWD=%s" % (
              "NetezzaSQL",self.host, self.database, self.user, self.password)
        #connect to a netezza database, you need ansi=True or it's all garbled
        return pyodbc.connect(connection_str, ansi=True)


class VerticaDB(DBConnectionWrapper):

    def __init__(self, wrap_name=None, user=None, password=None,
                 host=None, database=None):
        self.user = user
        self.password = password
        self.host = host
        self.database = database
        super(VerticaDB, self).__init__(wrap_name=wrap_name)

    def create_connection(self):
        """
        Override the create_connection from the VerticaDB
        class which get's called in it's initializer
        """
        import pyodbc
        connection_str=(
                        "DRIVER={%s};SERVER=%s;DATABASE=%s;UID=%s;PWD=%s"
                        %
                        ("VerticaSQL",self.host, self.database, self.user, self.password)
                       )
        #connect to a netezza database, you need ansi=True or it's all garbled
        return pyodbc.connect(connection_str, ansi=True)


class MysqlDB(DBConnectionWrapper):

    def __init__(self, wrap_name=None, user=None, password=None,
            host=None, database=None, port=defaults.MYSQL_DEFAULT_PORT,
            autocommit=True):
        """
        A connection for a Mysql Database.  Requires that
        MySQLdb is installed

        :param user: your user name for that database
        :param password: Your password to the database
        :param host: host name or ip of the database server
        :param database: name of the database on that server
        """
        self.user = user
        self.password = password
        self.host = host
        self.database = database
        self.port=port
        self.autocommit = autocommit
        super(MysqlDB, self).__init__(wrap_name=wrap_name)

    def create_connection(self):
        """
        Override the create_connection from the DbConnectionWrapper
        class which get's called in it's initializer
        """
        import MySQLdb.connections
        import MySQLdb.converters
        import MySQLdb

        # make it so that it uses floats instead of those Decimal objects
        # these are really slow when trying to load into numpy arrays and
        # into pandas
        conv = MySQLdb.converters.conversions.copy()
        conv[MySQLdb.constants.FIELD_TYPE.DECIMAL] = float
        conv[MySQLdb.constants.FIELD_TYPE.NEWDECIMAL] = float
        conn = MySQLdb.connect(host=self.host, user=self.user,
                               db=self.database, passwd=self.password,
                               conv=conv, port=self.port)
        if self.autocommit:
            conn.autocommit(True)
        return conn

    def use(self, database):
        return self.select('use %s' % database).data

    def databases(self):
        return self.select('show databases').data

    def tables(self):
        return self.select('show tables').data

    def now(self):
        # not sure that the [0][0] will always be true...but it works now
        return self.select('select now()').data[0][0]

    @property
    def command(self):
        """
        Here is the command for doing the mysql command
        """
        return  'mysql -A -u %s -p%s -h %s %s' % (self.user, self.password,
                                                     self.host, self.database)


class PostgresDB(DBConnectionWrapper):

    def __init__(self, wrap_name=None, user=None, password=None,
                 host=None, database=None, port=defaults.POSTGRES_DEFAULT_PORT,
                 readonly=False, autocommit=False):
        """
        A connection for a Postgres Database.  Requires that
        psycopg2 is installed

        :param user: your user name for that database
        :param password: Your password to the database
        :param host: host name or ip of the database server
        :param database: name of the database on that server
        """
        self.user = user
        self.password = password
        self.host = host
        self.database = database
        self.port = port
        self.readonly = readonly
        self.autocommit = autocommit
        super(PostgresDB, self).__init__(wrap_name=wrap_name)

    def create_connection(self):
        """
        Override the create_connection from the DbConnectionWrapper
        class which get's called in it's initializer
        """
        import psycopg2

        # make it so that it uses floats instead of those Decimal objects
        # these are really slow when trying to load into numpy arrays and
        # into pandas
        DEC2FLOAT = psycopg2.extensions.new_type(
                    psycopg2.extensions.DECIMAL.values,
                        'DEC2FLOAT',
                            lambda value, curs: float(value) if value is not None else None)
        psycopg2.extensions.register_type(DEC2FLOAT)

        conn = psycopg2.connect(host=self.host, port=self.port,  user=self.user,
                                    password=self.password, database=self.database )

        # If this is a read-only connection, then force autocommit as well
        if self.readonly:
            conn.set_session(autocommit=True, readonly=True)
        # Else, set the autocommit
        else:
            conn.set_session(autocommit=self.autocommit)

        return conn

    def use(self, database):
        return self.select('use %s' % database).data

    def databases(self):
        return self.select('select distinct table_catalog, table_schema from information_schema.tables').data

    def tables(self):
        return [ x[0] for x in self.select('select table_name from information_schema.tables where table_schema = (select current_schema())').data ]

    def now(self):
        # not sure that the [0][0] will always be true...but it works now
        return self.select('select now()').data[0][0]

    def __call__(self, query = None, outfile= None):
        """
        Create a shell connection to this mysql instance
        """
        cmd = 'psql -U %s -W%s -h %s %s %s' % (self.user, self.password,
                                                     self.host, self.port, self.database)
        self.run_command(cmd)


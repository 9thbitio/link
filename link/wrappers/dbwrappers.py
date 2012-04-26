from link import Wrapper
from link.utils import list_to_dataframe

class DBConnectionWrapper(Wrapper):
    """
    wraps a database connection and extends the functionality
    to do tasks like put queries into dataframes
    """
    def __init__(self, wrap_name = None, **kwargs):
        
        if kwargs:
            self.__dict__.update(kwargs)

        #get the connection and pass it to wrapper os the wrapped object
        connection = self.create_connection()
        super(DBConnectionWrapper, self).__init__(wrap_name, connection)
    
    def execute(self, query):
        """
        Creates a cursor and executes the query for you
        """
        cursor = self._wrapped.cursor()
        cursor.execute(query)
        return cursor

    #TODO: Add in the ability to pass in params and also index 
    def select_dataframe(self, query):
        """
        Select everything into a datafrome with the column names
        being the names of the colums in the dataframe
        """
        try:
            from pandas import DataFrame
        except:
            raise Exception("pandas required to select dataframe. Please install"  + 
                            "sudo easy_install pandas")

        cursor = self.execute(query)
        data = cursor.fetchall()
        columns = [x[0].lower() for x in cursor.description]
        
        #check to see if they have duplicate column names
        if len(columns)>len(set(columns)):
            raise Exception("Cannot have duplicate column names " +
                            "in your query %s, please rename" % columns)
        return list_to_dataframe(data, columns) 
    
    def select(self, query):
        """
        Run a select and just return everything. If you have pandas installed it
        is better to use select_dataframe if you want to do data manipulation
        on the results
        """
        cursor = self.execute(query)
        data = cursor.fetchall()
        return data
 
    def create_connection(self):
        """
        Override this function to create a depending on the type
        of database

        :returns: connection to the database you want to use
        """
        pass


class SqliteDBConnectionWrapper(DBConnectionWrapper):
    """
    A connection wrapper for a sqlite database
    """
    def __init__(self, wrap_name=None, path=None, create_db = True):
        """
        A connection for a SqlLiteDb.  Requires that sqlite3 is
        installed into python

        :param path: Path to the sqllite db
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
        import sqlite3
        db = sqlite3.connect(self.path)
        return db

    def __call__(self):
        """
        Run's the command line sqlite application
        """
        self.run_command('sqlite3 %s' % self.path)


class MysqlDBConnectionWrapper(DBConnectionWrapper):

    def __init__(self, wrap_name=None, user=None, password=None, 
                 host=None, database=None):
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
        super(MysqlDBConnectionWrapper, self).__init__(wrap_name=wrap_name)

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
                               conv=conv)
        return conn

    def __call__(self, query = None, outfile= None):
        """
        Create a shell connection to this mysql instance
        """
        cmd = 'mysql -A -u %s -p%s -h %s %s' % (self.user, self.password,
                                                     self.host, self.database)
        self.run_command(cmd)


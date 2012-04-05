from link import Wrapper


class DBConnectionWrapper(Wrapper):
    """
    wraps a database connection and extends the functionality
    to do tasks like put queries into dataframes
    """
    def __init__(self, wrap_name = None, db_type=None, 
                 user=None, password=None, host=None, path=None):
        self.db_type = db_type
        self.user = user
        self.password = password
        self.host = host
        self.path = path
        #get the connection and pass it to wrapper os the wrapped object
        connection = self.create_connection()
        super(DBConnectionWrapper, self).__init__(wrap_name, connection)
    
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
        return DataFrame(data, columns=columns)
    
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



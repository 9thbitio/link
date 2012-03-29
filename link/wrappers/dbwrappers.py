from link import Wrapper

class ConnectionWrapper(Wrapper):
    """
    wraps a database connection and extends the functionality
    to do tasks like put queries into dataframes
    """
    def __init__(self, wrap_name = None, db_type=None, user=None, password=None,
                 host=None, path=None):
        self.db_type = db_type
        self.user = user
        self.password = password
        self.host = host
        self.path = path
        #get the connection and pass it to wrapper os the wrapped object
        connection = self._get_connection()
        super(ConnectionWrapper, self).__init__(wrap_name, connection)
    
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
        columns = [x[0] for x in cursor.description]
        
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
 
    def _get_connection(self):
        """
        Connect to different types of databases that
        are configured.  Note, everytime you call connection it
        will be a brand new connection
        """

        db_type = self.db_type

        if db_type =='sqlite':
            return self._connect_sqlite(self.path)

        raise Exception("No such db_type %s " % db_type)

    def _connect_sqlite(self, path_to_db):
        """
        Connect a sqlite database
        """
        import sqlite3
        db = sqlite3.connect(path_to_db)
        return db



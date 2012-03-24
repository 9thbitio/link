from pandas import DataFrame
from link import Linker

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
        self._connection = None
        super(ConnectionWrapper, self).__init__(wrap_name)

    def __getattr__(self, name):
        """
        Trick for using functionality of the connection
        """
        try:
            return self.__getattribute__(name)
        except:
            return self.connection.__getattribute__(name)

    def select_dataframe(self, query):
        """
        Select everything into a datafrome with the column names
        being the names of the colums in the dataframe
        """
        cursor = self.execute(query)
        data = cursor.fetchall()
        columns = [x[0] for x in cursor.description]
        return DataFrame(data, columns=columns)

    @property
    def connection(self):
        """
        Connect to different types of databases that
        are configured.  Note, everytime you call connection it
        will be a brand new connection
        """
        #if there is already a connection just return it
        if self._connection:
            return self._connection

        db_type = self.db_type

        if db_type =='sqlite':
            self._connection = self.connect_sqlite(self.path)
        #if there is no connection db_type throw an error
        else:
            raise Exception("No such db_type %s " % db_type)

        return self._connection

    def connect_sqlite(self, path_to_db):
        """
        Connect a sqlite database
        """
        import sqlite3
        db = sqlite3.connect(path_to_db)
        return ConnectionWrapper(db)


class DbLink(Linker):
    """
    encapsualates database connections
    """
    def __init__(self):
        super(DbLink, self).__init__('dbs', ConnectionWrapper)



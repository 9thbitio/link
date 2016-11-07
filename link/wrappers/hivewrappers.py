import contextlib

from link import Wrapper
from link.utils import list_to_dataframe
from datetime import datetime
from .dbwrappers import DBConnectionWrapper, DBCursorWrapper

class HiveCursorWrapper(Wrapper):
    """
    Wraps a select and makes it easier to tranform the data
    """
    def __init__(self, cursor, query=None, wrap_name=None):
        import pandas as pd
        #ghetto, but we make the assumption that pandas is not required
        self.nat = pd.NaT
        self.nan = pd.np.nan
        self.cursor = cursor
        self._data = None
        self._columns = None
        self._dtypes = None
        self.query = query
        super(HiveCursorWrapper, self).__init__(wrap_name, cursor)
    
    @property
    def data(self):
        if not self._data:
            data = []
            # Hive doesn't like fetching large amounts of data
            while True:
                rows = self.cursor.fetchN(500)
                if not len(rows):
                    break
                data += map(self._parse_row, rows)
            
            self._data = data

        return self._data

    @property 
    def columns(self):
        if not self._columns:
            schema = self.cursor.getThriftSchema()
            self._columns = [field.name for field in schema.fieldSchemas]

        return self._columns

    @property 
    def dtypes(self):
        if not self._dtypes:
            schema = self.cursor.getThriftSchema()
            self._dtypes = [field.type for field in schema.fieldSchemas]

        return self._dtypes
    
    def _return_type(self, item, dtype):
        if dtype == 'timestamp':
            try:
                return datetime.strptime(item, '%Y-%m-%d %H:%M:%S')
            except:
                return self.nat
        
        if dtype in ('double', 'float'):
            if item.lower() == 'null':
                return self.nan
            return float(item)

        elif dtype in ('i8', 'i16', 'i32', 'i64'):
            if item.lower() == 'null':
                return self.nan
            return int(item)

        return item

    def _parse_row(self, row):
        vals = row.split('\t')
        dtypes = self.dtypes
        return [self._return_type(item, dtype) for item, dtype in zip(vals,
                                                                      dtypes)]
    def _create_dict(self, row):
        return dict(zip(self.columns, row)) 

    def as_dict(self):
        return map(self._create_dict, self.data)

    def as_dataframe(self, chunk_size = None):
        try:
            from pandas import DataFrame
        except:
            raise Exception("pandas required to select dataframe. "
                            "Please install: sudo pip install pandas")
        
        if chunk_size:
            rows = self.cursor.fetchN(chunk_size)
            data = map(self._parse_row, rows)
            return list_to_dataframe(data, self.columns)

        return list_to_dataframe(self.data, self.columns)

    def __iter__(self):
        return self.data.__iter__()

    def __call__(self, query=None):
        """
        Creates a cursor and executes the query for you.
        """
        query = query or self.query
        self.cursor.execute(query)

        return self

class HiveDB(Wrapper):
    """
    wraps a database connection and extends the functionality
    to do tasks like put queries into dataframes
    """
    def __init__(self, wrap_name=None, host=None, port=None, database='default'):
        
        self.host = host
        self.port = port
        self.database = database
        # get the connection and pass it to wrapper as the wrapped object
        connection = self.create_connection()
        self.client = self.create_client(connection)
        # connection becomes wrapped object
        super(HiveDB, self).__init__(wrap_name, connection)
        self._use(database)

    def _execute(self, query):
        """
        Executes the query for you, without opening or closing connection.
        """
        return HiveCursorWrapper(self.client, query)()

    def execute(self, query):
        """
        Executes the query for you, leaving connection open.
        """
        self._wrapped.open()
        return self._execute(query)

    def select_dataframe(self, query):
        """
        Select everything into a datafrome with the column names
        being the names of the colums in the dataframe
        """
        try:
            from pandas import DataFrame
        except:
            raise Exception("pandas required to select dataframe. "
                            "Please install: sudo pip install pandas")

        self._wrapped.open()  
        cursor = self._execute(query)
        df = cursor.as_dataframe()
        self._wrapped.close()
        return df
    
    def select(self, query=None, chunk_name=None):
        """
        Run a select and just return everything. If you have pandas installed it
        is better to use select_dataframe if you want to do data manipulation
        on the results
        """
        self._wrapped.open() 
        cursor = self._execute(query)
        data = cursor.data
        self._wrapped.close()
        return data

    def create_client(self,connection):
        """
        Creates a Hive client.
        """
        from hive_service import ThriftHive
        from thrift.protocol import TBinaryProtocol
        
        protocol = TBinaryProtocol.TBinaryProtocol(connection)
        return ThriftHive.Client(protocol)
 
    def create_connection(self):
        """
        Create connection to Hive server.
        """
        from thrift.transport import TSocket
        from thrift.transport import TTransport

        transport = TSocket.TSocket(self.host, self.port)
        return TTransport.TBufferedTransport(transport)

    def _use(self, database):
        try:
            assert database in self.databases()
            out = self.select('use %s' % database)
        except AssertionError:
            return False

        return len(out) == 0

    def use(self, database):
        if self._use(database):
            self.database = database
            return 'switched to %s' % database
        else:
            return '%s not a valid database' % database

    def databases(self):
        self._wrapped.open()
        dbs = self.client.get_all_databases()
        self._wrapped.close()
        return dbs

    def tables(self):
        self._wrapped.open()
        tables = self.client.get_all_tables(self.database)
        self._wrapped.close()
        return tables

#keep it backwards compatible for now
HiveConnectionWrapper = HiveDB

class Hive2Cursor(DBCursorWrapper):

    @property
    def data(self):
        self._data = []
        
        #probably a faster way to do this
        if not self._data:
            next_data = self.cursor.fetch() 

            while(next_data):
                self._data.extend(next_data)
                next_data = self.cursor.fetch() 

        return self._data

    @property
    def columns(self):
        if not self._columns:
            self._columns = [x['columnName'].lower() for x in self.cursor.getSchema()]
        return self._columns
 

class Hive2DB(DBConnectionWrapper):
    
    CURSOR_WRAPPER = Hive2Cursor

    def __init__(self, wrap_name=None, user='', password='', 
                 host='', database='default', port = 10000, 
                 auth_mechanism = "PLAIN"):
        self.user = str(user)
        self.password = str(password)
        self.host = str(host)
        self.database = str(database)
        self.port = port
        self.auth_mechanism = auth_mechanism
        super(Hive2DB, self).__init__(wrap_name=wrap_name)

    def create_connection(self):
        """
        Override the create_connection from the Netezza 
        class which get's called in it's initializer
        """
        import pyhs2
        conn = pyhs2.connect(host=self.host, 
                             port=self.port,
                             authMechanism=self.auth_mechanism, 
                             user=self.user, 
                             password=self.password, 
                             database=self.database)
        return conn



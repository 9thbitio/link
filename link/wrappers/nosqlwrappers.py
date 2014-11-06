from link import Wrapper
from link.utils import list_to_dataframe

class NoSqlDB(Wrapper):
    """
    wraps a database connection and extends the functionality
    to do tasks like put queries into dataframes
    """
    def __init__(self, wrap_name = None, **kwargs):
        
        if kwargs:
            self.__dict__.update(kwargs)

        #get the connection and pass it to wrapper os the wrapped object
        connection = self.create_connection()
        super(NoSqlConnectionWrapper, self).__init__(wrap_name, connection)
   
    def set_table(self, table):
        self.table = table
    
    def get_current_table(self, table=None):
        """
        """
        if table:
            return table
        if self.table:
            return self.table
        raise Exception("No table defined or no default table")

    def get(self, key, table=None):
        """
        get the row or rows from a table (could do cool things with rows by
        allowing for regex or searches
        """
        pass
    
    def put(self, key, column, value, table=None):
        """
        put a key or keys back to the nosqldb
        """
        pass

    def _host_to_hostport(self, host):
        """
        turn your host into a (host, port) combo 
        """
        #need to figure out the standard db port
        (ret_host, ret_port) = ("", 8080)
        host_info = host.split(":")
        if len(host_info)>1:
            ret_port = host_info[1]
        ret_host = host_info[0]
        return (ret_host, int(ret_port))

    def create_connection(self):
        """
        Override this function to create a depending on the type
        of database

        :returns: connection to the database you want to use
        """
        pass

NoSqlConnectionWrapper = NoSqlDB

class HbaseDB(NoSqlConnectionWrapper):
    """
    A connection wrapper for a sqlite database
    """
    #from hbase import Hbase 

    def __init__(self, wrap_name=None, host=None, version='0.92'):
        """
        A connection for a SqlLiteDb.  Requires that sqlite3 is
        installed into python

        :param host: the host:port of the hbase thrift server
        """
        self.version = version
        (self.host, self.port) = self._host_to_hostport(host)
        
        # TODO: Where would one configure the default port for link
        super(HbaseNoSqlConnectionWrapper, self).__init__(wrap_name=wrap_name)

    def create_connection(self):
        """
        Override the create_connection from the DbConnectionWrapper
        class which get's called in it's initializer
        """
        import happybase 
        return happybase.Connection(self.host,
                                         port=self.port,compat=self.version)

    def __call__(self):
        """
        Run's the command line sqlite application
        """
        self.run_command('hbase shell')

HbaseNoSqlConnectionWrapper = HbaseDB

class MongoDB(NoSqlConnectionWrapper):
    """
    A connection wrapper for a sqlite database
    """
    def __init__(self, wrap_name=None, host=None, port=None, **kwargs):
        """
        MongoDB wrapper to connect to mongo

        :param host: the host:port of the hbase thrift server
        """
        (self.host, self.port) = (host, port) 
        self.params = kwargs
        
        # TODO: Where would one configure the default port for link
        super(MongoDB, self).__init__(wrap_name=wrap_name)

    def create_connection(self):
        """
        Override the create_connection from the DbConnectionWrapper
        class which get's called in it's initializer
        """
        from pymongo import Connection
        return Connection(self.host, port=self.port, **self.params)

    def __call__(self):
        """
        Run's the command line sqlite application
        """
        self.run_command('mongo')


class CassandraDB(NoSqlConnectionWrapper):
    """
    A connection wrapper for a sqlite database
    """
    def __init__(self, wrap_name=None, nodes=None, default_fetch_size=None, **kwargs):
        """
        CassandraDB wrapper to connect to a Cassandra cluster

        :param nodes: a list of nodes to use for initial connection
        """
        self.nodes = nodes
        self.params = kwargs
        self.default_fetch_size=default_fetch_size

        # TODO: Where would one configure the default port for link
        super(CassandraDB, self).__init__(wrap_name=wrap_name)

    def create_connection(self):
        """
        Override the create_connection from the DbConnectionWrapper
        class which get's called in it's initializer
        """
        from cassandra.cluster import Cluster
        from cassandra.query import dict_factory

        session = Cluster(self.nodes).connect()
        
        # Don't return paged results
        session.default_fetch_size = self.default_fetch_size
        
        # Return in dictionary format for easy parsing to DataFrame
        session.row_factory = dict_factory

        return session

    def __call__(self):
        """
        Run's the command line sqlite application
        """
        self.run_command('cqlsh')

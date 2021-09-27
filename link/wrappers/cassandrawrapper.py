import time

from link import Wrapper
from link.exceptions import LNKAttributeException
from link.utils import pd


class CassandraResultsetWrapper(Wrapper):
    max_retries = 5

    def __init__(self, result):
        self.result = result

    @property
    def columns(self):
        return self.result.column_names

    @property
    def dtypes(self):
        return self.result.column_types

    def as_dataframe(self):
        """Convert query result rows to pandas dataframe.
        """
        if pd is None:
            raise RuntimeError('pandas is required to use dataframes')

        from cassandra import DriverException
        df = pd.DataFrame()
        data = self.result
        while True:
            for retry in range(self.max_retries):
                try:
                    df = df.append(pd.DataFrame(columns=data.column_names, data=(list(row) for row in data.current_rows)))
                    break
                except DriverException:
                    if retry >= self.max_retries - 1:
                        raise
                    time.sleep(2 ** retry)
            if data.has_more_pages:
                data.fetch_next_page()
            else:
                break
        return df

    def __iter__(self):
        return self.result.__iter__()


class CassandraDB(Wrapper):
    """Wrapper for Cassandra database.

    Requires cassandra-driver package. For compression to work (highly recommended) lz4 system library is required.

    Sample config entry:
        "my_cassandra": {
            "wrapper": "CassandraDB",
            "nodes": ["localhost"],
            "user": "john_doe",
            "password": "secret_word",
            "keyspace": "mydb",
            "default_fetch_size": 10000
        }
    """
    max_retries = 5  # auto-retry failed operations

    def __init__(self, wrap_name=None, **kwargs):
        self._columns = None
        self._data = None
        if kwargs:
            self.__dict__.update(kwargs)
        super(self.__class__, self).__init__(wrap_name)
        self.connection = self.create_connection()

    def execute(self, query, args=()):
        """Execute query.
        """
        return self.connection.execute(query, args)

    def select(self, query, params=()):
        """Execute select query and return result set.

        Do not use for queries that modify the data - autoretry may mess it up!
        """
        from cassandra.query import SimpleStatement
        from cassandra import ConsistencyLevel, DriverException

        statement = SimpleStatement(query)
        statement.consistency_level = ConsistencyLevel.ONE
        for retry in range(self.max_retries):
            try:
                return CassandraResultsetWrapper(self.execute(query, params))
            except DriverException:
                if retry >= self.max_retries - 1:
                    raise
                time.sleep(2 ** retry)

    def select_dataframe(self, query, args=()):
        """Return query result as pandas DataFrame.
        """
        return self.select(query, args).as_dataframe()

    def create_connection(self):
        """Connect to Cassandra cluster and return connection handle.
        """
        from cassandra.auth import PlainTextAuthProvider
        from cassandra.cluster import Cluster
        from cassandra.policies import RoundRobinPolicy

        if self.user is not None:
            auth_provider = PlainTextAuthProvider(username=self.user, password=self.password)
        else:
            auth_provider = None
        cluster = Cluster(
            self.nodes, load_balancing_policy=RoundRobinPolicy(), auth_provider=auth_provider, compression=True
        )
        conn = cluster.connect(self.keyspace)
        try:
            conn.default_fetch_size = self.default_fetch_size
        except LNKAttributeException:
            pass
        return conn

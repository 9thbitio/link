from link import Wrapper


class PrestoDB(Wrapper):
    """
    Wraps a PrestoDB connection and extends the functionality
    to do tasks like select queries into dataframes
    """

    def __init__(self, wrap_name=None, host=None, port=None, user=None, catalog=None, database='default'):

        self.host = host
        self.port = port
        self.user = user
        self.catalog = catalog
        self.database = database
        # get the connection and pass it to wrapper as the wrapped object
        self.connection = self.create_connection()
        # connection becomes wrapped object
        super(PrestoDB, self).__init__(wrap_name, self.connection)

    def select_dataframe(self, query):
        """
        Select everything into a dataframe with the column names
        being the names of the columns in the dataframe
        """
        try:
            import pandas as pd
        except:
            raise Exception("pandas required to select dataframe.")

        df = pd.read_sql(query, self.engine)
        return df

    def create_connection(self):
        """
        Create connection to Presto server.
        """
        try:
            from sqlalchemy.engine import create_engine
            import requests
            import pyhive
        except:
            raise Exception("pyhive, sqlalchemy and requests required to select dataframe.")

        engine = create_engine('presto://{presto_hostname}:{presto_port}/{presto_catalog}/{presto_database}'
                               .format(presto_hostname=self.host,
                                       presto_port=self.port,
                                       presto_catalog=self.catalog,
                                       presto_database=self.database))
        return engine

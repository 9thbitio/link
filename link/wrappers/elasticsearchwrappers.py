from link import Wrapper
from link.utils import list_to_dataframe

class ElasticSearch(Wrapper):
    """
    wraps an ElasticSearch connection and extends the functionality
    to do tasks like put queries into dataframes
    """
    def __init__(self, wrap_name = None, **kwargs):
        if kwargs:
            self.__dict__.update(kwargs)

        #get the connection and pass it to wrapper os the wrapped object
        connection = self.create_connection()
        super(ElasticSearch, self).__init__(wrap_name, connection)

    def search(self, query):
        """
        Search through ElasticSearch records and return the result as dict
        """
        response = self._wrapped.search(
            index = self.index,
            doc_type = self.doc_type,
            body = query,
        )
        return response

    def index(self, doc):
        """
        Add a new entry to ElasticSearch index
        """
        ret = self._wrapped.index(
            index=self.index,
            doc_type=self.doc_type,
            body=doc,
        )

    def create_connection(self):
        """
        Override the create_connection from the Wrapper
        class which get's called in it's initializer
        """
        from elasticsearch import Elasticsearch
        return Elasticsearch(hosts=self.hosts)

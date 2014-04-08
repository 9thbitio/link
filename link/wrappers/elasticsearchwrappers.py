from link import Wrapper
from link.utils import list_to_dataframe

class ElasticSearch(Wrapper):
    """
    wraps an ElasticSearch connection and extends the functionality
    to do tasks like put queries into dataframes
    """
    def __init__(self, wrap_name = None, **kwargs):
        self.options = {}
        if kwargs:
            self.options.update(kwargs)

        #get the connection and pass it to wrapper os the wrapped object
        connection = self.create_connection()
        super(ElasticSearch, self).__init__(wrap_name, connection)

    def search(self, query):
        """
        Search through ElasticSearch records and return the result as dict
        """
        response = self._wrapped.search(
            index = self.options['index'],
            doc_type = self.options['doc_type'],
            body = query,
        )
        return response

    def scan(self, query, chunk_size=10000, scroll='10m'):
        """
        Query ElasticSearch records, suitable for large response.

        Similar to 'search' method but works better with large result sets
        (hundreds of thousands of records) as it receives data from
        ElasticSearch in chunks.

        Returns generator object which can be used to grow Pandas
        DataFrame iteratively, e.g.:

        df = DataFrame()
        for response in esdb.scan(query):
            df = pandas.concat([df, DataFrame(response['hits']['hits'])])
        # do something with df here

        """
        from elasticsearch.exceptions import TransportError
        response = self._wrapped.search(
            index=self.options['index'],
            doc_type = self.options['doc_type'],
            body = query,
            search_type = 'scan',
            scroll = scroll,
            size=chunk_size,
        )
        scroll_id = response['_scroll_id']
        while True:
            try:
                response = self._wrapped.scroll(scroll_id=scroll_id, scroll=scroll)
                yield response
            except TransportError as e:
                break

    def index(self, doc):
        """
        Add a new entry to ElasticSearch index
        """
        response = self._wrapped.index(
            index=self.options['index'],
            doc_type=self.options['doc_type'],
            body=doc,
        )
        return response

    def create_connection(self):
        """
        Override the create_connection from the Wrapper
        class which get's called in it's initializer
        """
        from elasticsearch import Elasticsearch
        return Elasticsearch(hosts=self.options['hosts'])

"""
apilink contains all of the classes that you need to connect to a configured
api.  It wraps the python requests package, and provides some helpful functions
that make it easy to parse json and xml responses
"""
import requests
from requests.auth import HTTPBasicAuth
from functools import wraps
import json
from xml.etree import cElementTree as ET
from link import Wrapper
from link.wrappers import APIResponseWrapper

class GraphiteResponseWrapper(APIResponseWrapper):
    """
    """

    def __init__(self, wrap_name = None, response = None):
        self._json = None
        self._xml = None
        super(GraphiteResponseWrapper, self).__init__(wrap_name, response)

    def parse(self):
        """
        make the data into a parsed hash 
        """
        datasets = self.content.split("\n")
        data = [(self._parse_header(sets.split("|")[0]),self._parse_data(sets.split("|")[1])) for sets in datasets if len(sets) > 0]
        time = self._parse_time_range(datasets[0].split("|")[0])

        return dict([("timestamp",time)] + data)

    def _parse_time_range(self,head_str):
        min, max = (int(i) for i in head_str.split(",")[1:3])
        step = int(head_str.split(",")[3])
        return range(min,max,step)
        
    def _parse_header(self,head_str):
        return head_str.split(",")[0]

    def _parse_data(self,data_str):
        return [0 if elem == 'None' else float(elem) for elem in data_str.split(",")]

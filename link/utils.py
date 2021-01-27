import os
from functools import partial

import six

from itertools import chain, repeat

if six.PY3:
    izip = zip
else:
    from itertools import izip
# -*- coding: utf-8 -*-

"""
link.utils
~~~~~~~~~~~~

Commonly used utility functions in the link code

:copyright: (c) 2013 by David Himrod
:license: Apache2, see LICENSE for more details.

"""

def load_json_file(file_name):
    """
    given a file name this function will json decode it and
    return a dictionary
    """
    try:
        data = open(file_name, 'r').read()
    except:
        raise Exception("No such file %s" % file_name)

    import json
    try:
        return json.loads(data)
    except Exception as e:
        raise ValueError("Error json decoding file: %s error: %s" % (file_name,
                                                                     e.message))

def list_to_dataframe(rows, names):
    """
    Turns a rows of data into a dataframe and gives them the column names
    specified

    :params rows: the data you want to put in the dataframe
    :params names: the column names for the dataframe
    """
    from pandas import DataFrame
    col_convert_func = None
    try:
        import pandas._tseries as lib
        col_convert_func = lib.convert_sql_column
    except ImportError:
        import pandas.lib as lib
        try:
            col_convert_func = lib.convert_sql_column
        except:
            col_convert_func = partial(lib.maybe_convert_objects, try_float=1)

    if isinstance(rows, tuple):
        rows = list(rows)

    columns = dict(zip(names, lib.to_object_array_tuples(rows).T))

    if col_convert_func is not None:
        for k, v in six.iteritems(columns):
            columns[k] = col_convert_func(v)

    return DataFrame(columns, columns=names)



def array_pagenate(n, iterable, padvalue=None):
    """
    takes an array like [1,2,3,4,5] and splits it into even chunks.  It will
    pad the end with your default value to make fully even.  
    """
    return izip(*[chain(iterable, repeat(padvalue, n-1))]*n)

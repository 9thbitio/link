import os

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
    except:
        raise Exception("Error json decoding file %s" % file_name)

def list_to_dataframe(rows, names):
    from pandas.version import version
    if version < '0.8.0':
        import pandas._tseries as lib
    else:
        import pandas.lib as lib
    from pandas import DataFrame

    if isinstance(rows, tuple):
        rows = list(rows)

    columns = dict(zip(names, lib.to_object_array_tuples(rows).T))

    for k, v in columns.iteritems():
        columns[k] = lib.convert_sql_column(v)

    return DataFrame(columns, columns=names)

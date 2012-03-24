import os

def json_load_file(file_name):
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

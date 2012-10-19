#!/usr/bin/python
from flask import Flask, request, json, Response
from link import lnk

app = Flask(__name__)

#lnk server uses link to go get a link
db = lnk.lnk.configuration_db.configuration
#this is the actual configuration collection that we will be using most
user_config = db.user_config

@app.errorhandler(404)
def page_not_found(e):
    return '{"error":"NOTFOUND", "error_msg":"api not found"}', 404
        
@app.errorhandler(500)
def internal_error(e):
    #TODO: Log out the errors to somewhere useful
    return '{"error":"UNKNOWN"}', 500

@app.route("/status", methods=['GET'])
def status():
    """
    Check to see which badges they have
    """
    return '{"status":"ok"}'
 
@app.route("/configure", methods=['POST'])
def configure():
    """
    Get configuration for this user and password
    """
    j = request.json

    if j is None:
        return '{"error":"NOJSON"}'

    print j 
    user = j.get('user')
    password = j.get('password')
    print user
    config = user_config.find_one({'user':user})
    #pop off the id that mongo gives it
    if config:
        config.pop('_id')
    else:
        config = {}

    return json.dumps(config) 

def remove_mongo_id(data):
    """
    Remove _id incase they pass it in
    """
    if data.has_key('_id'):
        return data.pop('_id')

@app.route("/edit", methods=['POST'])
def edit():
    """
    Get configuration for this user and password
    """
    j = request.json

    if j:
        user = j.get('user')
        if not user:
            return '{"error":"NOUSERSPECIFIED"}'
        remove_mongo_id(j)
        #don't want it overwriting things like the id
        config = user_config.find_one({'user':user})

        #if its already there then just overwrite it
        #not sure this is the behavior i want
        if not config:
            return '{"error":"NOSUCHUSER"}'
        
        #update the config.  At some point we may want to make this different
        #because it doesn't allow for deletion very easily
        config.update(j)
        user_config.save(config)

        return '{"status":"ok"}'

    return '{"error":"NOJSONDATA"}'


@app.route("/new", methods=['POST'])
def new():
    """
    Get configuration for this user and password
    """
    j = request.json
    if j:
        user = j.get('user')

        if not user:
            return '{"error":"NOUSERSPECIFIED"}'

        #don't want it overwriting things like the id
        remove_mongo_id(j)
        config = user_config.find_one({'user':user})

        if config:
            return '{"error":"USEREXISTS", "error_msg":"Try /edit to edit an existing user}'

        user_config.save(j)
        return '{"status":"ok"}'

    return '{"error":"NOJSONDATA"}'


if __name__ == "__main__":
    import sys
    debug = False
    if len(sys.argv)>1:
        debug = sys.argv[1] == 'debug'

    app.run(debug=debug , host='0.0.0.0')

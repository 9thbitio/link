#!/usr/bin/python
from __future__ import absolute_import
from flask import Flask, request, json, Response
from .link import lnk, Wrapper
from subprocess import Popen, signal

app = Flask(__name__)

class LnkServer(Wrapper):
    """
    The lnk server connects to the underlying configuration database and can
    get, alter and create user configs.  It is also where the authentication is
    done
    """
    def __init__(self, wrap_name = None, host='localhost', port=5000):
        self.host = host
        self.port = port
        self.process = None
        super(LnkServer, self).__init__(wrap_name)

    def start(self, host=None, port=None, background=False, debug=False):
        """
        Start the configuration server on the host and port.  Probably need to
        revisit this. 
        """
        import sys
        
        host = host or self.host
        port = port or self.port

        #TODO: need to have a test that checks for lnk_dir
        from .link import lnk_dir
        
        if debug:
            debug = 'debug'
        else:
            debug = ''

        #cmd = '%s/scripts/server.py %s' % (lnk_dir, debug)

        cmd = ['%s/scripts/server.py' % (lnk_dir), debug]
        self.process=Popen(cmd)
        #if its not background then let's wait for it
        if not background:
            self.process.wait()

        return self.process

    def stop(self):
        """
        Stop this server.
        """
        #TODO: If you are using debug server it starts a second process 
        # and the kill does not kill that one
        if self.process:
            self.process.kill()
            self.process.wait()
            self.process = None
            return True
        return False

    def connection(self):
        """
        Returns a connection to the server 
        """
        pass

    def __del__(self):
        """
        Not sure if i need this
        """
        self.stop()

try:
    #if it's configure then we can use it
    lnk_server = lnk.lnk.server 
except:
    lnk_server = LnkServer()


from link import lnk
from subprocess import Popen, PIPE, STDOUT

class VirtualLink(object):

    def __init__(self, config_file=None, namespace=None):
        """
        Create a new instance of the Link.  Should be done
        through the instance() method.
        """
        self._on=False
 
    def on(self):
        self._on = True

    def hello(self):
        print "hello"

    def runcommand(self, cmd, *kargs, **kwargs):
        """
        Allows you to run a command that is either a configured one
        or the run action of a wrapper you have configured
        """
        try:
            lnk(cmd).run(*kargs, **kwargs)
        except Exception as e:
            p = Popen(cmd,shell=True)
            p.wait()

vlnk = VirtualLink()

from link import Wrapper
import logging
import sys
import logging.handlers

class LogWrapper(Wrapper):
    """
    Wraps the logging class to allow for special types of calls like alerting
    """
    def __init__(self, wrap_name = None, log_name=None,  
                 message_format="%(asctime)s - %(levelname)s - %(message)s",
                 level = logging.WARN, log_path=None):

        self.log = logging.getLogger(log_name)
        address='/dev/log'
        if sys.platform == "darwin":
            address = "/var/run/syslog"

        handler =logging.handlers.SysLogHandler(address=address)
        handler.setFormatter(logging.Formatter(message_format))
        self.log.addHandler(handler)
        super(LogWrapper, self).__init__(wrap_name, self.log)


#class LogLink(Linker):
    #"""
    #Links your logging with your 'logs' configuration.  Also
    #contains a singleton link to your syslog which can be used
    #through out your program and across files
    #"""
    #SYSTEM_LOG = None

    #def __init__(self):
        #super(LogLink, self).__init__('logs')

    #@classmethod
    #def sys_log(cls):
        #"""
        #Get the system log which is a singleton log that goes to
        #/var/log/..
        #"""
        #if not cls.SYSTEM_LOG:
            #cls.SYSTEM_LOG = LogWrapper("__SYSTEM_LOG__")
        #return cls.SYSTEM_LOG

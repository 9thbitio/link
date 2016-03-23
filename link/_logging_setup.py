import logging
import logging.config
from inspect import getouterframes, currentframe

class LogHandler(object):
    """
    Class that sets up logging (optionally from a conf) and allows you to log to files,
    stdout, etc...
    """

    def __init__(self, conf={}, verbose=False):
        """
        :param dict conf: optional, logging configuration defined in link.config under
            top-level key "msg"
        :param bool verbose: whether to set verbose logging. This will add a handler that
            prints INFO and higher level to stdout
        """
        self._set_up_logging(conf, verbose)

    def _set_up_logging(self, conf, verbose):
        if conf:
            logging.config.dictConfig(conf)

            # Currently, any handlers you specify in the link.config will have their
            # Formatters overriden with the standardized one provided below.
            frmt = self._log_format()
            for handler in logging.getLogger('').handlers:
                handler.setFormatter(frmt)

        # If you have either specified verbose logging, or no logging configuration was
        # provided, verbose logging (to stdout) will be enabled.
        if verbose or not conf:
            self._set_up_verbose_logging()
        return

    def _log_format(self):
        """
        Defines a standard Timestamp to add to all logs: Year-Month-Day Hour:Min:Sec
        """
        msg_format = "%(asctime)s %(levelname)s %(message)s"
        date_format = '%Y-%m-%d %H:%M:%S'
        frmt = logging.Formatter(msg_format, date_format)
        return frmt

    def _set_up_verbose_logging(self):
        """
        Attaches a handler to root logger that writes to stdout.
        """
        import sys
        verbose_hndlr = logging.StreamHandler(stream=sys.stdout)
        verbose_hndlr.setFormatter(self._log_format())
        verbose_hndlr.setLevel(logging.DEBUG)

        root = logging.getLogger('')
        root.addHandler(verbose_hndlr)
        root.setLevel(logging.INFO)
        return

    def debug(self, msg, exc_info=False):
        self.write(msg, level=logging.DEBUG, exc_info=exc_info)

    def info(self, msg, exc_info=False):
        self.write(msg, level=logging.INFO, exc_info=False)

    def warn(self, msg, exc_info=False):
        self.write(msg, level=logging.WARN, exc_info=exc_info)

    def error(self, msg, exc_info=False):
        self.write(msg, level=logging.ERROR, exc_info=exc_info)

    def crit(self, msg, exc_info=False):
        self.write(msg, level=logging.CRITICAL, exc_info=exc_info)

    def write(self, msg, level=logging.INFO, exc_info=False, extras=None):
        self._write(msg, level, exc_info, extras)

    def _write(self, msg, level, exc_info, extras=None):
        # Attach filename and line number of caller to the log (from ``inspect`` module)
        # calling frame is 3 up
        caller_info = getouterframes(currentframe())[3]
        # Get filename from full path
        caller_file = caller_info[1].split('/')[-1]
        # And line number
        lineno = caller_info[2]

        body = "{}:{} {}".format(caller_file, lineno, msg)

        logging.log(level, body, exc_info=exc_info)


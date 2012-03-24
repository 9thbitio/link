from functools import wraps

class DebugWrapper():
    """
    wraps nose.  I want to make it so it can distribute out unittesting
    to multiple cores.
    """
    def listen(_self,func):
        """
        Makes it so you can listen in on the contents of the function
        call
        """
        @wraps(func)
        def debug_function(*kargs, **kwargs):
            ret = {}
            ret['kwargs'] = kwargs
            ret['kargs'] = kargs
            ret['function'] = func
            return ret

        return debug_function

    def inspect(_self,func):
        """
        Makes it so you can listen in on the contents of the function
        call
        """
        @wraps(func)
        def debug_function(*kargs, **kwargs):
            ret = {}
            ret['kwargs'] = kwargs
            ret['kargs'] = kargs
            ret['function'] = func
            ret['result'] = func(*kargs, **kwargs)
            return ret

        return debug_function


class DebugLink(DebugWrapper):
    """
    Links you or your nose wrappers
    """
    def links(self):
        return DebugWrapper()

    def __call__(self):
        return self.links()


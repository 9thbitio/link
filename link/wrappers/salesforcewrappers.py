
from link import Wrapper

class SalesForceWrapper(Wrapper):

    def __init__(self, wrap_name = None, base_url=None, user=None,
                 password=None, token=None):

        self.base_url = base_url
        self.user = user
        self.password = password
        self.token = token
        self.service = self._auth_service()
        super(SalesForceWrapper, self).__init__(wrap_name, self.service)
    
    def _auth_service(self):
        import beatbox
        service = beatbox.PythonClient()
        service.login(self.user, "{}{}".format(self.password, self.token))
        return service



import server.exception


HTTP_METHODS = ['get', 'post', 'put', 'delete', 'options', 'head', 'patch']


class Endpoint(object):

    url = '/'

    def get(self, request):
        self._method_not_allowed()

    def post(self, request):
        self._method_not_allowed()

    def put(self, request):
        self._method_not_allowed()

    def delete(self, request):
        self._method_not_allowed()

    def options(self, request):
        self._method_not_allowed()

    def head(self, request):
        self._method_not_allowed()

    def patch(self, request):
        self._method_not_allowed()

    def _method_not_allowed(self):
        raise server.exception.RestfulException(405, 'method not allowed')

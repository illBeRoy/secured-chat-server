import server.exception


HTTP_METHODS = ['get', 'post', 'put', 'delete', 'options', 'head', 'patch']


class Endpoint(object):
    '''
    Declares an endpoint to be instated by the server.
     
    Each of the methods below represents a handler that is automatically registered as a flask route.
    
    Whenever a route is invoked, a new Endpoint instance is created. Therefore, endpoint classes CAN be stateful.
    '''

    # the url for which the methods will be registered.
    # supports uri types and regexes, much like a flask route.
    # uri parts are passed as keyword arguments to the handlers.
    url = '/'

    def get(self, request, **uri_parts):
        self._method_not_allowed()

    def post(self, request, **uri_parts):
        self._method_not_allowed()

    def put(self, request, **uri_parts):
        self._method_not_allowed()

    def delete(self, request, **uri_parts):
        self._method_not_allowed()

    def options(self, request, **uri_parts):
        self._method_not_allowed()

    def head(self, request, **uri_parts):
        self._method_not_allowed()

    def patch(self, request, **uri_parts):
        self._method_not_allowed()

    def _method_not_allowed(self):
        raise server.exception.RestfulException(405, 'method not allowed')

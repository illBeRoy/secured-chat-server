import server


class Endpoint(server.Endpoint):

    url = '/users'

    def post(self, request):
        return self.a()

    def a(self):
        #request = inspect.getouterframes(inspect.currentframe())[1][0].f_locals['request']
        return {'method': "ok"}

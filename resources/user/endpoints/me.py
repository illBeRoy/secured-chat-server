import server
from resources.user.authentication import authenticate


class Endpoint(server.Endpoint):

    url = '/users/me'

    @authenticate
    def get(self):
        return self.auth.user.username

import server
import resources.user.models
from resources.user.authentication import authenticate


class Endpoint(server.Endpoint):

    url = '/users/friends'

    @authenticate
    def get(self):
        querystring_parser = server.QuerystringParser()
        querystring_parser.add_argument('username', help='name of the friend to find', required=True)
        querystring = querystring_parser.parse_args()

        try:
            user = self.session.query(resources.user.models.User) \
                .filter(resources.user.models.User.username == querystring.username) \
                .limit(1).all()[0]
        except Exception:
            raise server.RestfulException(404, 'user not found')

        return user.render()



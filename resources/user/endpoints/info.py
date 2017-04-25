import server
from resources.user.authentication import authenticate


class Endpoint(server.Endpoint):

    url = '/users/info'

    @authenticate
    def post(self):
        body_parser = server.BodyParser()
        body_parser.add_argument('info', help='user private info, such as contacts list', required=True)
        body = body_parser.parse_args()

        self.auth.user.info = body.info

        try:
            self.session.add(self.auth.user)
            self.session.commit()
        except:
            raise server.RestfulException(409, 'could not save info')

        return self.auth.user.render(with_private_fields=True)

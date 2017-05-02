import server
from resources.user.authentication import authenticate


class Endpoint(server.Endpoint):

    url = '/users/me'

    @authenticate
    def get(self):
        return self.auth.user.render(with_private_fields=True)

    @authenticate
    def post(self):
        # parse body
        body_parser = server.BodyParser()
        body_parser.add_argument('info', help='user private info, such as contacts list')
        body = body_parser.parse_args()

        # since it is not mandatory to change any of the user's fields, this flag will indicate whether it has
        user_changed = False

        # if info passed, apply to user
        if body.info is not None:
            self.auth.user.info = body.info
            user_changed = True

        # if user has not changed anything, do not continue. it is not mandatory to change any one field, but it is
        # required to alter at least one - otherwise, the `get` method should be used
        if not user_changed:
            raise server.RestfulException(400, 'the request did not contain any user updates. ' +
                                               'if you wish to just view it, please use the `get` method.')

        # save changes to db
        try:
            self.session.add(self.auth.user)
            self.session.commit()
        except:
            raise server.RestfulException(409, 'could not save info')

        # return user
        return self.auth.user.render(with_private_fields=True)

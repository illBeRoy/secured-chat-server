import server
import resources.user.models


class Endpoint(server.Endpoint):

    url = '/users'

    def post(self):
        # parse request
        body_parser = server.BodyParser()
        body_parser.add_argument('username', help='unique name of user', required=True)
        body_parser.add_argument('password', help='desired password', required=True)
        body_parser.add_argument('private_key', help='secret rsa key of user (encrypted)', required=True)
        body_parser.add_argument('public_key', help='public rsa key of user (plain)', required=True)
        args = body_parser.parse_args()

        # instantiate new user
        user = resources.user.models.User(args.username, args.password, args.private_key, args.public_key)
        self.session.add(user)

        # attempt to commit
        try:
            self.session.commit()
        except server.IntegrityError:
            raise server.RestfulException(400, resources.user.models.User.integrity_fail_reasons)

        # return success
        return user.render(), 201

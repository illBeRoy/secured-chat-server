import server
import resources.user.models


def authenticate(func):
    '''
    The authentication decorator is meant for resources which would like to authenticate an incoming request.
    
    If successful, a `user` object will be attached to the instance.
     
    :param func: endpoint handler
    '''

    def wrapped(self, *args, **kwargs):
        header_parser = server.HeadersParser()
        header_parser.add_argument('x-user-name', help='name of the user to authenticate', required=True)
        header_parser.add_argument('x-user-token', help='authentication token as set in registration', required=True)
        args = header_parser.parse_args()

        try:
            user = self.session.query(resources.user.models.User).filter(username=args.x_user_name).limit(1).all()[0]

            if user.check_password(args.x_user_token):
                self.auth = object()
                self.auth.user = user
                return func(self, *args, **kwargs)
            else:
                raise Exception('wrong password')
        except:
            raise server.RestfulException(401, 'unauthorized')

    return wrapped

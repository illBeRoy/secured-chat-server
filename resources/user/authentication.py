import server
import resources.user.models


def authenticate(func):
    '''
    The authentication decorator is meant for resources which would like to authenticate an incoming request.
    
    If successful, a `user` kwarg is supplied to the endpoint.
     
    :param func: endpoint handler
    '''

    def wrapped(*args, **kwargs):
        header_parser = server.HeadersParser()
        header_parser.add_argument('x-user-name', help='name of the user to authenticate', required=True)
        header_parser.add_argument('x-user-token', help='authentication token as set in registration', required=True)
        args = header_parser.parse_args()

        try:
            user = resources.user.models.User.query.filter(username=args.x_user_name)[0]
        except:
            raise server.RestfulException(401, 'unauthorized')

        if user.check_password(args.x_user_token):
            return func(*args, user=user, **kwargs)
        else:
            raise server.RestfulException(401, 'unauthorized')

    return wrapped

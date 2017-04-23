import server
import resources.user.models
import collections


def authenticate(func):
    '''
    The authentication decorator is meant for resources which would like to authenticate an incoming request.
    
    If successful, a `user` object will be attached to the instance.
     
    :param func: endpoint handler
    '''

    def wrapped(self, *args, **kwargs):
        # parse headers
        header_parser = server.HeadersParser()
        header_parser.add_argument('x-user-name', help='name of the user to authenticate', required=True)
        header_parser.add_argument('x-user-token', help='authentication token as set in registration', required=True)
        header_args = header_parser.parse_args()

        try:
            # try to get user
            user = self.session.query(resources.user.models.User) \
                               .filter(resources.user.models.User.username == header_args.x_user_name) \
                               .limit(1).all()[0]

            # check password
            if user.check_password(header_args.x_user_token):
                self.auth = Auth(user=user)
            else:
                raise Exception('wrong password')

        except:
            # if failed for any reason, raise unauthorized
            raise server.RestfulException(401, 'unauthorized')

        finally:
            return func(self, *args, **kwargs)

    return wrapped


class Auth(object):
    '''
    A struct that contains authentication information, to be used by the endpoint.
    '''

    def __init__(self, user=None):
        self._user = user

    @property
    def user(self):
        return self._user

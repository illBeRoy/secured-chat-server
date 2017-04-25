import os
import re
import base64
import hashlib
import server


class User(server.Model):

    username = server.ModelField(server.ModelTypes.String(32), unique=True)
    password = server.ModelField(server.ModelTypes.String(44))
    salt = server.ModelField(server.ModelTypes.String(44))
    private_key = server.ModelField(server.ModelTypes.String(4096))
    public_key = server.ModelField(server.ModelTypes.String(4096))
    info = server.ModelField(server.ModelTypes.String(4096))

    renders_fields = ['username', 'public_key']
    renders_private_fields = ['private_key', 'info']

    assert_fail_reasons = 'bad username, should be alphanumeric, not shorter than 3 and not longer than 32 characters'
    integrity_fail_reasons = 'username is already in use'

    allowed_usernames = re.compile('^[a-zA-Z0-9_-]{3,32}$')

    def __init__(self, username, password, private_key, public_key, info=None):
        assert User.allowed_usernames.match(username)

        self.username = username
        self.salt = self._create_salt()
        self.password = self._hash_with_salt(password, self.salt)
        self.private_key = private_key
        self.public_key = public_key
        self.info = info or ''

    def check_password(self, password):
        if self.password == self._hash_with_salt(password, self.salt):
            return True

        return False

    def render(self, with_private_fields=False, **kwargs):
        user = super(User, self).render(**kwargs)

        if with_private_fields:
            for field in User.renders_private_fields:
                user[field] = getattr(self, field)

        return user

    def _create_salt(self):
        '''
        Generates a base64 encoded 128bit long cryptographically random salt.
        '''
        return base64.b64encode(os.urandom(16))

    def _hash_with_salt(self, str, salt):
        '''
        Creates a sha256 hash from a pair of string and salt.
        
        :param str: the source string
        :param salt: hashing salt
        '''
        salted_str = '{0}{1}'.format(str, salt)
        return base64.b64encode(hashlib.sha256(salted_str).digest())

import server


class Message(server.Model):

    from_user = server.ModelField(server.ModelTypes.Integer, info='User.id')
    to_user = server.ModelField(server.ModelTypes.Integer, info='User.id')
    contents = server.ModelField(server.ModelTypes.String())
    sent_at = server.ModelField(server.ModelTypes.Date())

    renders_fields = ['from_user', 'to_user', 'contents', 'sent_at']

    def __init__(self, username, password, private_key, public_key):
        self.username = username
        self.salt = self._create_salt()
        self.password = self._hash_with_salt(password, self.salt)
        self.private_key = private_key
        self.public_key = public_key

    def check_password(self, password):
        if self.password == self._hash_with_salt(password, self.salt):
            return True

        return False

    def render(self, with_private_fields=False, **kwargs):
        user = super(User, self).render(**kwargs)

        if with_private_fields:
            user['private_key'] = self.private_key

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

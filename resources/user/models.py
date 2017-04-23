import os
import base64
import hashlib
import server


class User(server.Model):

    username = server.ModelField(server.ModelTypes.String(32), unique=True)
    password = server.ModelField(server.ModelTypes.String(44))
    salt = server.ModelField(server.ModelTypes.String(44))
    private_key = server.ModelField(server.ModelTypes.String(4096))
    public_key = server.ModelField(server.ModelTypes.String(4096))

    integrity_fail_reason = 'username is already in use'

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

    def _create_salt(self):
        '''
        Generates a base64 encoded 32bit long cryptographically random salt.
        '''
        return base64.b64encode(os.urandom(32))

    def _hash_with_salt(self, str, salt):
        '''
        Creates a sha256 hash from a pair of string and salt.
        
        :param str: the source string
        :param salt: hashing salt
        '''
        salted_str = '{0}{1}'.format(str, salt)
        return base64.b64encode(hashlib.sha256(salted_str).digest())

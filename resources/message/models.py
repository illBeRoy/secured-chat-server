import time

import server
from resources.user.models import User


class Message(server.Model):

    from_user = server.ModelField(User.UsernameType)
    to_user = server.ModelField(User.UsernameType)
    contents = server.ModelField(server.ModelTypes.String(4096))
    sent_at = server.ModelField(server.ModelTypes.Integer)

    renders_fields = ['from_user', 'to_user', 'contents', 'sent_at']
    integrity_fail_reasons = 'message is either sent by or sent to nonexistent users'
    assert_fail_reasons = 'cannot send a message '

    def __init__(self, from_user, to_user, contents):
        self.from_user = from_user
        self.to_user = to_user
        self.contents = contents
        self.sent_at = int(time.time())

        assert from_user != to_user

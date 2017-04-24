import time

import server


class Message(server.Model):

    from_user = server.ModelField(server.ModelTypes.ForeignKey('users.id'))
    to_user = server.ModelField(server.ModelTypes.ForeignKey('users.id'))
    contents = server.ModelField(server.ModelTypes.String(4096))
    sent_at = server.ModelField(server.ModelTypes.Integer)

    renders_fields = ['from_user', 'to_user', 'contents', 'sent_at']
    integrity_fail_reasons = 'message is either sent by or sent to nonexistent users'

    def __init__(self, from_user, to_user, contents):
        self.from_user = from_user
        self.to_user = to_user
        self.contents = contents
        self.sent_at = int(time.time())

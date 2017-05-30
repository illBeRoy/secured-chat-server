import time

import server
import resources.user
import resources.message.models


class Endpoint(server.Endpoint):

    url = '/messages'

    @resources.user.authenticate
    def get(self):
        # remember the time where the query has started
        query_time = time.time()

        # fetch all messages
        messages = self.session.query(resources.message.models.Message) \
                    .filter(resources.message.models.Message.to_user == self.auth.user.username) \
                    .order_by(resources.message.models.Message.sent_at.desc()) \
                    .limit(100) \
                    .all()

        # return relevant messages and query time
        return {'query_time': int(query_time),
                'messages': [message.render() for message in messages]}

    @resources.user.authenticate
    def post(self):
        # parse request
        body_parser = server.BodyParser()
        body_parser.add_argument('recipient', help='username of the recipient', required=True)
        body_parser.add_argument('contents', help='contents of the message', required=True)
        body = body_parser.parse_args()

        # get user by username
        try:
            user = self.session.query(resources.user.models.User) \
                .filter(resources.user.models.User.username == body.recipient) \
                .limit(1).all()[0]
        except Exception:
            raise server.RestfulException(404, 'user not found')

        # create message
        try:
            message = resources.message.models.Message(self.auth.user.username, user.username, body.contents)
            self.session.add(message)
            self.session.commit()

        except server.IntegrityError:
            raise server.RestfulException(400, resources.message.models.Message.integrity_fail_reasons)

        except AssertionError:
            raise server.RestfulException(400, resources.message.models.Message.assert_fail_reasons)

        # return success
        return message.render(), 201

    @resources.user.authenticate
    def delete(self):
        querystring_parser = server.QuerystringParser()
        querystring_parser.add_argument('until', help='timestamp of the last query time', required=True)
        querystring = querystring_parser.parse_args()

        try:
            query_timestamp = int(querystring.until)
        except:
            raise server.RestfulException(400, 'invalid field "until": valid unix timestamp expected')

        deleted_count = self.session.query(resources.message.models.Message) \
                                    .filter(resources.message.models.Message.to_user == self.auth.user.username,
                                            resources.message.models.Message.sent_at < query_timestamp) \
                                    .delete()

        return {'result': 'success', 'deleted': deleted_count}

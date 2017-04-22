import server


class Endpoint(server.Endpoint):

    url = '/users/<int:id>'

    def post(self, request, id=0):
        querystring_parser = server.QuerystringParser()
        querystring_parser.add_argument('age', required=True)
        headers = querystring_parser.parse_args()
        #
        # body_parser = server.BodyParser()
        # body_parser.add_argument('age', type=int, required=True)
        # body = body_parser.parse_args()
        #
        # return {'roysom': headers.roysom, 'chernima': headers.chernima, 'avivbh': headers.avivbh, 'age': body.age}
        return {'a': headers.age}

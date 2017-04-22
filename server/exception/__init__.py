class RestfulException(Exception):

    def __init__(self, status, message):
        super(RestfulException, self).__init__('[{0}] {1}'.format(status, message))
        self._status = status
        self._message = message

    @property
    def status(self):
        return self._status

    @property
    def message(self):
        return self._message

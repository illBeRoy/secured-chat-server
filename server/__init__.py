import functools
import flask
import sqlalchemy

from endpoint import HTTP_METHODS, Endpoint
from parsers import BodyParser, HeadersParser, QuerystringParser
from exception import RestfulException
from model import Model, ModelField, ModelTypes


class Server(object):

    def __init__(self, *args, **kwargs):
        self._app = flask.Flask(*args, **kwargs)
        self._app.errorhandler(404)(functools.partial(self._error_handler, 404, 'not found'))
        self._sqlengine = None

    def run(self, port, debug=False):
        # initialize sql
        Model.metadata.create_all(self._sqlengine)

        # start flask server
        self._app.run('0.0.0.0', port, debug)

    def use_db(self, url):
        self._sqlengine = sqlalchemy.create_engine(url)

    def use_resource(self, resource):
        # add endpoints
        for endpoint in dir(resource.endpoints):
            endpoint_module = getattr(resource.endpoints, endpoint)
            if hasattr(endpoint_module, 'Endpoint'):
                endpoint_class = getattr(endpoint_module, 'Endpoint')
                self._register_endpoint('{0}.{1}'.format(resource, endpoint), endpoint_class)

        # prepare models
        for model in dir(resource.models):
            possible_model_class = getattr(resource.models, model)
            if isinstance(possible_model_class, Model):
                possible_model_class.__tablename__ = '{0}s'.format(possible_model_class.__name__.lower())

    def _register_endpoint(self, name, cls):
        for method in HTTP_METHODS:
            self._app.add_url_rule(cls.url,
                                   '{0}.{1}'.format(name, method),
                                   view_func=functools.partial(self._endpoint_handler, cls, method),
                                   methods=[method])

    def _endpoint_handler(self, endpoint_cls, method, **uri_params):
        try:
            endpoint_instance = endpoint_cls()
            return flask.jsonify(getattr(endpoint_instance, method)(flask.request, **uri_params))

        except RestfulException as err:
            return self._error_handler(err.status, err.message, err)

        except Exception as err:
            return self._error_handler(500, err.message, err)

    def _error_handler(self, status, message, err=None):
        return flask.jsonify({'status': status, 'message': message}), status

import collections
import flask

import server.exception


class _RequestParser(object):
    '''
    RequestParser is a declarative interface to describe the parameters expected by an endpoint handler.
    
    It is very similar in form to argparse.ArgumentParser().
    
    This is an internal baseclass, and cannot be used outside.
    '''

    # the source string represents the part of the request used for supplying the arguments for a given class.
    # it is used by several exceptions in order to denote to the user where they went wrong when building their
    # request. meant to be overriden.
    source = 'request'

    def __init__(self):
        self._arguments = {}

    def add_argument(self, name, help='', type=object, required=False, default=None):
        '''
        Adds an argument declaration to the current parser.
        
        :param name: name of the argument 
        :param help: internal explanation as for the argument's nature
        :param type: the expected type of the value
        :param required: whether or not this argument MUST be passed in the request
        :param default: default value, in case this argument was not passed in the request
        '''

        if name in self._arguments:
            raise Exception('Argument {0} defined more than once.'.format(name))

        self._arguments[name] = {'help': help, 'type': type, 'required': required, 'default': default}
        self._validate_rule(name, self._arguments[name])

    def parse_args(self):
        '''
        Parses the request and extracts the declared arguments.
        
        :return: an object whose fields match the expected arguments 
        '''

        ParsedArguments = collections.namedtuple('ParsedArguments',
                                                 [argname.replace('-', '_') for argname in self._arguments.keys()])

        argument_values = []
        for arg_name, arg_rule in self._arguments.iteritems():
            arg_val = self._get_argument_value(arg_name)

            if arg_val is None:
                arg_val = arg_rule['default']

            if arg_val is None and arg_rule['required']:
                raise server.exception.RestfulException(400, 'field "{0}": required in {1} but not found'.format(arg_name, self.source))

            if arg_val is not None and not isinstance(arg_val, arg_rule['type']):
                raise server.exception.RestfulException(400, 'field "{0}": wrong type. expected: {1}'.format(arg_name,
                                                                                                           arg_rule['type'].__name__))

            argument_values.append(arg_val)

        return ParsedArguments(*argument_values)

    def _validate_rule(self, argument_name, rule):
        '''
        After compiling a rule supplied in add_argument, makes sure that it has no conflicts.
        
        Some parsers can override this method in order to add their own validations.
        
        :param argument_name: name of the argument matching the rule 
        :param rule: the rule, as built by add_argument
        '''

        if rule['required'] and rule['default'] is not None:
            raise Exception('Invalid argument {0}: cannot be "required" and have default value.'.format(argument_name))

    def _get_argument_value(self, name):
        '''
        When parsing arguments, this method provides an interface to get an argument's value from the request.
        
        Parsers implement this method according to the part of the request they refer to. 
        
        :param name: name of the parameter to fetch
        '''
        raise NotImplementedError('Internal class: Please use one of the parser subclasses instead.')


class BodyParser(_RequestParser):
    '''
    This parser is used for parsing a request's body.
    '''

    source = 'body'

    def _get_argument_value(self, name):
        try:
            return flask.request.get_json(force=True).get(name)
        except:
            return None


class _TypelessRequestParser(_RequestParser):
    '''
    A RequestParser that does not provide type validation.
    
    Used for parsers which handle all-string sources.
    '''

    def _validate_rule(self, argument_name, rule):
        super(_TypelessRequestParser, self)._validate_rule(argument_name, rule)

        if rule['type'] != object:
            raise Exception('Invalid argument {0}: {1} arguments cannot have types.'.format(argument_name, self.source))


class HeadersParser(_TypelessRequestParser):
    '''
    This parser is used for parsing a request's headers.
    '''

    source = 'headers'

    def _get_argument_value(self, name):
        try:
            return flask.request.headers.get(name)
        except:
            return None


class QuerystringParser(_TypelessRequestParser):
    '''
    This parser is used for parsing a request's query string args.
    '''

    source = 'querystring'

    def _get_argument_value(self, name):
        try:
            return flask.request.args.get(name)
        except:
            return None

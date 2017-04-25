import unittest
import os
import os.path
import collections
import shutil
import time
import subprocess
import requests
import tinylog


class SanityTestCase(unittest.TestCase):
    '''
    This a sanity check for the server.
    
    It ensures that the server is working correctly from various aspects:
     1. registration and user naming rules
     2. messaging
     3. access control and authentication
     
    In order to perform the tests, an sqlite database file is created, and the server executable is being
    run as subprocess. Requests are then being made to the local server and the results are asserted.
    After each test, both the server and the database are being tore down, in order to prevent contamination.
    '''

    executable_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..')
    assets_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'tmp')
    server_port = 12000

    AuthenticatedUser = collections.namedtuple('AuthenticatedUser', ['data', 'send'])

    def setUp(self):
        self._logger = tinylog.Logger(console='stdout')

        self._logger.critical('Starting test: {0}'.format(self._testMethodName))
        self._create_assets_path()
        self._server_instance = self._create_server_instance()
        self._await_server_up()

    def tearDown(self):
        self._logger.critical('Tearing down test: {0}'.format(self._testMethodName))
        self._kill_server_instance()
        self._clear_assets_path()

    def _create_assets_path(self):
        '''
        Creates assets path for testing session.
        '''
        self._logger.debug('Creating assets path')

        try:
            os.makedirs(SanityTestCase.assets_path)
        except:
            raise Exception('Assets directory already exists, previous tests were probably not successfully tore down.')

    def _clear_assets_path(self):
        '''
        Removes assets path to prevent contamination. 
        '''
        self._logger.debug('Removing assets path')

        try:
            shutil.rmtree(SanityTestCase.assets_path)
        except:
            raise Exception('Could not remove assets directory post test.')

    def _create_server_instance(self):
        '''
        Creates server process. 
        '''
        self._logger.debug('Starting server process')

        db_file = os.path.join(SanityTestCase.assets_path, 'db.sqlite')

        server_instance = subprocess.Popen('./start.py -p {0} -db "sqlite:///{1}"'.format(SanityTestCase.server_port,
                                                                                          db_file),
                                           shell=True,
                                           cwd=SanityTestCase.executable_path,
                                           stdout=subprocess.PIPE,
                                           stderr=subprocess.PIPE)

        return server_instance

    def _kill_server_instance(self):
        '''
        Kills server process.
        '''
        self._logger.debug('Killing server process')
        self._server_instance.kill()

    def _await_server_up(self, timeout=20):
        '''
        Polls the server until it is up or the test times out. 
        '''
        while timeout > 0:
            try:
                requests.get('http://localhost:{0}'.format(SanityTestCase.server_port))
                return True
            except:
                timeout -= 1
                time.sleep(0.5)

    def _send_request(self, method, url, headers=None, params=None, body=None, expected_status=None):
        '''
        Sends a request to the server.
        
        :param method: http method 
        :param url: endpoint url
        :param headers: request headers (optional)
        :param params: request parameters (optional)
        :param body: request body (optional)
        :param expected_status: if set, will assert against the response status, otherwise checks for 2xx. (optional) 
        :return: body of the response
        '''
        url = url if url.startswith('/') else '/{0}'.format(url)

        self._logger.debug('Sending request: {0} [{1}]'.format(url, method.upper()))

        request = getattr(requests, method)
        response = request('http://localhost:{0}{1}'.format(SanityTestCase.server_port, url),
                           headers=headers,
                           params=params,
                           json=body)

        if expected_status is not None:
            self.assertEqual(response.status_code, expected_status)
        else:
            self.assertGreaterEqual(response.status_code, 200)
            self.assertLess(response.status_code, 300)

        return response.json()

    def _send_request_as(self, username, password):
        '''
        Creates a function that can send an authenticated request.
        
        :param username: name of the authenticated user 
        :param password: password of the authenticated user
        :return: a function that performs request with the specified credentials
        '''

        # define auth method wrapper that adds credentials automatically
        def auth_req(*args, **kwargs):
            kwargs['headers'] = kwargs.get('headers', {})
            kwargs['headers']['x-user-name'] = username
            kwargs['headers']['x-user-token'] = password

            return self._send_request(*args, **kwargs)

        # return chain object
        return auth_req

    def _assert_response(self, response, expected_response, ignore_fields=('id',)):
        '''
        Asserts response jsons, while taking into account that some fields are not important.
        
        :param response: the received response
        :param expected_response: the expected dict
        :param ignore_fields: a list or tuple containing fields that should be ignored
        '''

        # copy response to conserve shallow input immutability
        response = dict(response)

        # remove unnecessary fields
        for field in ignore_fields:
            try:
                del response[field]
            except KeyError:
                raise Exception('Field \"{0}\" was expected in response but not found.'.format(field))

        # assert
        self.assertDictEqual(response, expected_response)

    def _register_user(self, username, password, confirm_response=True, **kwargs):
        '''
        Registers a user.
        
        :param username: name of the user 
        :param password: password of the user
        :param confirm_response: whether to assert that the response was successful or not 
        :param kwargs: extra args to pass to `self._send_request`
        :return: an authenticated user or the response (if confirm_response is False)
        '''
        self._logger.debug('Registering user: {0}'.format(username))

        req = {'username': username,
               'password': password,
               'public_key': 'public_key',
               'private_key': 'private_key'}

        res = self._send_request('post', '/users', body=req, **kwargs)

        if confirm_response:
            self._assert_response(res, {'username': username, 'public_key': 'public_key'})
            return SanityTestCase.AuthenticatedUser(data=res,
                                                    send=self._send_request_as(username, password))
        else:
            return res

    def _register_preset_users(self):
        '''
        Registers a set of preset users for tests that require mostly authenticated interaction.
        
        :return: a dictionary that contains users and credentials
        '''
        self._logger.debug('Registering preset users')

        users = {'roysom': self._register_user('roysom', 'bananas'),
                 'avivbh': self._register_user('avivbh', 'galil'),
                 'banuni': self._register_user('banuni', 'cyber')}

        return users

    def test_registration(self):
        '''
        Tests registration and authentication of user. 
        '''
        self._logger.info('Creating user in the system')
        user = self._register_user('roysom', 'bananas')

        self._logger.info('Checking user\'s profile')
        me = user.send('get', '/users/me')
        self._assert_response(me, {'username': 'roysom',
                                   'public_key': 'public_key',
                                   'private_key': 'private_key',
                                   'info': ''})

    def test_registration_multiple(self):
        '''
        Tests registration of multiple users and naming constraints. 
        '''
        self._logger.info('Creating users in the system')
        self._register_user('roysom', 'bananas')
        self._register_user('avivbh', 'galil')

        self._logger.info('Attempting to register user with bad name')
        self._register_user('roysom!@?$', 'apples', confirm_response=False, expected_status=400)

        self._logger.info('Attempting to register user with used name')
        self._register_user('roysom', 'apples', confirm_response=False, expected_status=400)

    def test_set_personal_info(self):
        user = self._register_user('roysom', 'bananas')

        self._logger.info('Updating personal info')
        response = user.send('post', '/users/info', body={'info': 'i am bea, i like tea'})
        self._assert_response(response,
                              {'username': 'roysom', 'info': 'i am bea, i like tea'},
                              ignore_fields=('id', 'private_key', 'public_key'))

        self._logger.info('Assuring persistence by getting own user profile')
        response = user.send('get', '/users/me')
        self._assert_response(response,
                              {'username': 'roysom', 'info': 'i am bea, i like tea'},
                              ignore_fields=('id', 'private_key', 'public_key'))

    def test_user_search(self):
        '''
        Tests user search.
        '''
        users = self._register_preset_users()

        self._logger.info('Testing search endpoint')
        res = users['roysom'].send('get', '/users/friends', params={'username': 'avivbh'})

        self._assert_response(res, {'username': 'avivbh',
                                    'public_key': 'public_key'})

    def test_send_message(self):
        '''
        Test sending messages between users, tenancy and deletion policy.
        '''
        users = self._register_preset_users()

        # send message
        self._logger.info('Sending a message from roysom to avivbh')
        users['roysom'].send('post', '/messages', body={'recipient': 'avivbh', 'contents': 'foo'})

        # wait a little bit
        time.sleep(1)

        # get message
        self._logger.info('Fetching message on aviv\'s end')
        aviv_messages = users['avivbh'].send('get', 'messages')

        # make sure only one message arrived, and that it contains the right contents
        self.assertEqual(len(aviv_messages['messages']), 1)
        self._assert_response(aviv_messages['messages'][0], {'contents': 'foo'}, ignore_fields=('id', 'sent_at'))

        # ensure that nadav has no messages, since no one sent him anything
        self._logger.info('Making sure that nadav is lonely and has no incoming messages')
        nuni_messages = users['banuni'].send('get', 'messages')
        self.assertEqual(len(nuni_messages['messages']), 0)

        # wait a little bit and send another message to aviv
        self._logger.info('Sending another message from roysom to avivbh')
        users['roysom'].send('post', '/messages', body={'recipient': 'avivbh', 'contents': 'bar'})

        # aviv deletes all read messages
        self._logger.info('Aviv deletes the messages that he already has')
        users['avivbh'].send('delete', '/messages', params={'until': aviv_messages['query_time']})

        # now make sure that he did not delete that one message he did not yet receive
        self._logger.info('Aviv tries to get more messages, make sure he gets whatever he did not yet read')
        aviv_messages = users['avivbh'].send('get', 'messages')

        # make sure that only the last message arrived, and that it contains the right contents
        self.assertEqual(len(aviv_messages['messages']), 1)
        self._assert_response(aviv_messages['messages'][0], {'contents': 'bar'}, ignore_fields=('id', 'sent_at'))

    def test_authentication_policy(self):
        '''
        Tests authentication policy: authenticated, unauthenticated and bad credentials
        '''
        user = self._register_user('inspector_gadget', 'foobarfoobar')

        self._logger.info('Testing request with correct credentials')
        user.send('get', 'messages')

        self._logger.info('Testing request without credentials')
        self._send_request('get', '/messages', expected_status=401)

        self._logger.info('Testing request with bad credentials')
        self._send_request_as('inspector_gadget', 'not right')('get', '/messages', expected_status=401)

    def test_penetration(self):
        '''
        Tests anonymous access to different api endpoints of the server.
        '''
        self._logger.info('Testing anonymous access attempts')

        endpoints = {'/users': {'post': 400}, # we're not gonna supply the right body here, so 400
                     '/users/me': {'get': 401},
                     '/users/friends': {'get': 401},
                     '/messages': {'post': 401, 'get': 401, 'delete': 401}}

        for endpoint, methods in endpoints.iteritems():
            for method, expected_status in methods.iteritems():
                self._send_request(method, endpoint, expected_status=expected_status)

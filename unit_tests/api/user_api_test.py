'''Unit tests for client_api.'''

import unittest

from persistence import user_models

from unit_tests.common import test_utils
test_utils.disable_require_oauth()

from api import user_api

import json


# pylint: disable=missing-docstring
class UserApiTest(test_utils.CommonNdbTest):
  '''A class to test client_api model.'''

  def setUp(self):
    test_utils.CommonNdbTest.setUp(self)
    test_utils.create_oauth_test_client()
    self.app = test_utils.create_flask_test_client(user_api)

  def test_get_user_returns_user_if_not_exists(self):
    # Setup.
    user = user_models.User(username='test_user')
    user.put()
    test_utils.mock_get_user_id(self, user.key.id())

    # Exercise.
    response = self.app.get('/api/user/me')

    # Verify
    self.assertEqual(200, response.status_code)
    user_json = json.loads(response.data)
    self.assertEqual('test_user', user_json['username'])

  def test_create_user_creates_if_not_exists(self):
    # Setup.
    headers = test_utils.create_basic_auth_headers()
    headers['Content-Type'] = 'application/json'

    user_data = json.dumps({'username': 'test_user'})

    # Exercise.
    response = self.app.post('/api/user/',
                             data=user_data,
                             headers=headers)

    # Verify
    self.assertEqual(200, response.status_code)
    user_json = json.loads(response.data)
    self.assertEqual('test_user', user_json['username'])
    self.assertTrue(user_models.User.find_by_username('test_user'))

  def test_create_user_finds_if_exists(self):
    # Setup.
    user = user_models.User(username='test_user')
    user.put()

    headers = test_utils.create_basic_auth_headers()
    headers['Content-Type'] = 'application/json'

    user_data = json.dumps({'username': 'test_user'})

    # Exercise.
    response = self.app.post('/api/user/',
                             data=user_data,
                             headers=headers)

    # Verify
    self.assertEqual(200, response.status_code)
    user_json = json.loads(response.data)
    self.assertEqual('test_user', user_json['username'])
    self.assertEqual(user.key.id(), user_json['user_id'])

  def test_create_user_fails_if_not_json(self):
    # Setup.
    headers = test_utils.create_basic_auth_headers()

    user_data = json.dumps({'username': 'test_user'})

    # Exercise.
    response = self.app.post('/api/user/',
                             data=user_data,
                             headers=headers)

    # Verify
    self.assertEqual(400, response.status_code)
    self.assertFalse(user_models.User.find_by_username('test_user'))

  def test_create_user_fails_if_not_authorized(self):
    # Setup.
    headers = {}
    headers['Content-Type'] = 'application/json'
    user_data = json.dumps({'username': 'test_user'})

    # Exercise.
    response = self.app.post('/api/user/',
                             data=user_data,
                             headers=headers)

    # Verify
    self.assertEqual(401, response.status_code)
    self.assertFalse(user_models.User.find_by_username('test_user'))


if __name__ == "__main__":
  unittest.main()
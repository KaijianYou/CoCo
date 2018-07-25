import unittest

from json import loads

from blog.app import create_app, db
from blog.utils.json_util import generate_success_json, generate_error_json
from blog.errors import PERMISSION_FORBIDDEN


class TestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('test')
        self.app_context = self.app.test_request_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_generate_success_json(self):
        result = {
            'nickname': 'panda',
            'email': 'panda@gmail.com',
            'id': 12
        }
        json_response = generate_success_json(result)
        result_json = loads(json_response.response[0])
        expected_result_json = {
            'status': 'OK',
            'data': {
                'nickname': 'panda',
                'email': 'panda@gmail.com',
                'id': 12
            }
        }
        self.assertEqual(result_json, expected_result_json)

    def test_generate_error_json(self):
        json_response = generate_error_json(PERMISSION_FORBIDDEN)
        error_json = loads(json_response.response[0])
        expected_error_json = {
            'status': 'ERROR',
            'errorCode': 'PERMISSION_FORBIDDEN',
            'errorMessage': '没有权限'
        }
        self.assertEqual(error_json, expected_error_json)


import unittest

from flask import jsonify
from json import loads

from blog.app import create_app, db
from blog.utils import generate_success_json, generate_error_json
from blog.errors import PermissionError


class TestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('test')
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_generate_success_json(self):
        result = {
            'username': 'tiger',
            'email': 'tiger@lion.com',
            'id': 12
        }
        json_response = generate_success_json(result)
        result_json = loads(json_response.response[0])
        expected_result_json = {
            'status': 'OK',
            'result': {
                'username': 'tiger',
                'email': 'tiger@lion.com',
                'id': 12
            }
        }
        self.assertEqual(result_json, expected_result_json)


    def test_generate_error_json(self):
        json_response = generate_error_json(PermissionError.Forbidden)
        error_json = loads(json_response.response[0])
        expected_error_json = {
            'status': 'ERROR',
            'errorCode': 'Forbidden',
            'errorMessage': '没有权限'
        }
        self.assertEqual(error_json, expected_error_json)

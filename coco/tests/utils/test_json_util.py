import unittest

from json import loads

from coco import create_app, db
from coco.utils.json_util import gen_success_json, gen_error_json
from coco.errors import PERMISSION_FORBIDDEN


class TestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('test')
        self.app_context = self.app.test_request_context()
        self.app_context.push()

    def tearDown(self):
        db.session.remove()
        self.app_context.pop()

    def test_gen_success_json(self):
        result = {
            'nickname': 'panda',
            'email': 'panda@gmail.com',
            'id': 12
        }
        json_response = gen_success_json(result)
        result_json = loads(json_response.response[0])
        expected_result_json = {
            'success': True,
            'data': {
                'nickname': 'panda',
                'email': 'panda@gmail.com',
                'id': 12
            }
        }
        self.assertEqual(result_json, expected_result_json)

    def test_gen_error_json(self):
        json_response = gen_error_json(PERMISSION_FORBIDDEN)
        error_json = loads(json_response.response[0])
        expected_error_json = {
            'success': False,
            'errorCode': 'PERMISSION_FORBIDDEN',
            'errorMessage': '没有权限'
        }
        self.assertEqual(error_json, expected_error_json)


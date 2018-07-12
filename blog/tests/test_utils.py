import unittest

from json import loads

from blog.app import create_app, db
from blog.models.user import User
from blog.models.article import Article
from blog.models.comment import Comment
from blog.models.tag import Tag
from blog.models.category import Category
from blog.utils import generate_success_json, generate_error_json, generate_fake_data
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

    def test_generate_fake_data(self):
        generate_fake_data(User)
        user_count = User.query.count()
        self.assertEqual(user_count, 10)

        generate_fake_data(Category, seed=1, total=1)
        categories = Category.query_all()
        self.assertEqual(len(categories), 1)
        self.assertEqual(categories[0].name, 'center')

        generate_fake_data(Tag, total=5)

        generate_fake_data(Article)
        generate_fake_data(Comment, total=20)
        comments = Comment.query_all()
        self.assertEqual(len(comments), 20)




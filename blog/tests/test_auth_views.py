import unittest

from flask import url_for, current_app

from blog.app import create_app, db
from blog.models.user import User, UserRole


class TestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('test')
        self.app_context = self.app.test_request_context()
        self.app_context.push()
        self.client = self.app.test_client(use_cookies=True)
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_login(self):
        url = url_for('auth.login')
        user = User.create(nickname='panda', email='panda@gmail.com', password='123456')

        # 用非法值登录
        response = self.client.post(url, data={'email': 'panda', 'password': '123456'})
        json_data = response.get_json()
        self.assertEqual(json_data['errorCode'], 'ILLEGAL_FORM')

        # 用错误的密码登录
        response = self.client.post(url, data={'email': 'panda@gmail.com', 'password': '345987'})
        json_data = response.get_json()
        self.assertEqual(json_data['errorCode'], 'WRONG_EMAIL_OR_PASSWORD')

        response = self.client.post(url, data={'email': 'panda@gmail.com', 'password': '123456'})
        json_data = response.get_json()
        self.assertEqual(json_data['status'], 'OK')

    def test_register(self):
        url = url_for('auth.register')
        # 两次输入的密码不一致
        response = self.client.post(
            url,
            data={
                'nickname': 'panda',
                'email': '666@gmail.com',
                'password': '123456',
                'password2': '234567'
            }
        )
        json_data = response.get_json()
        self.assertEqual(json_data['errorCode'], 'ILLEGAL_FORM')

        other_user = User.create(nickname='dog', email='dog@gmail.com', password='000000')
        response = self.client.post(
            url,
            data={
                'nickname': other_user.nickname,
                'email': 'panda@gmail.com',
                'password': '123456',
                'password2': '123456'
            }
        )
        json_data = response.get_json()
        self.assertEqual(json_data['errorCode'], 'NICKNAME_ALREADY_USED')

        response = self.client.post(
            url,
            data={
                'nickname': 'panda',
                'email': other_user.email,
                'password': '123456',
                'password2': '123456'
            }
        )
        json_data = response.get_json()
        self.assertEqual(json_data['errorCode'], 'EMAIL_ALREADY_REGISTERED')

        admin_email = current_app.config['ADMIN_EMAIL']
        response = self.client.post(
            url,
            data={
                'nickname': 'panda',
                'email': admin_email,
                'password': '123456',
                'password2': '123456'
            }
        )
        json_data = response.get_json()
        self.assertEqual(json_data['status'], 'OK')
        user = User.query_by_email(admin_email, is_enable=True)
        self.assertFalse(user is None)
        self.assertEqual(user.role, UserRole.ADMINISTRATOR)

    def test_logout(self):
        User.create(nickname='panda', email='panda@gmail.com', password='123456')
        response = self.client.post(
            url_for('auth.login'),
            data={'email': 'panda@gmail.com', 'password': '123456'}
        )
        json_data = response.get_json()
        self.assertEqual(json_data['status'], 'OK')

        response = self.client.get(url_for('auth.logout'))
        json_data = response.get_json()
        self.assertEqual(json_data['status'], 'OK')


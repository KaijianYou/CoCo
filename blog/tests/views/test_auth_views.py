import unittest

from flask import url_for, current_app

from blog.app import create_app, db
from blog.models.user import User, UserRole
from blog.utils.testing_utils import create_user_data


class TestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('test')
        self.app_context = self.app.test_request_context()
        self.app_context.push()
        self.client = self.app.test_client(use_cookies=True)
        db.create_all()
        create_user_data()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_login(self):
        url = url_for('auth.login')
        response = self.client.post(url, data={'email': 'panda@gmail.com', 'password': '123456'})
        json_data = response.get_json()
        self.assertEqual(json_data['status'], 'OK')

    def test_login_with_wrong_password(self):
        url = url_for('auth.login')
        response = self.client.post(url, data={'email': 'panda@gmail.com', 'password': '345987'})
        json_data = response.get_json()
        self.assertEqual(json_data['errorCode'], 'WRONG_EMAIL_OR_PASSWORD')

    def test_login_with_invalid_form_value(self):
        url = url_for('auth.login')
        response = self.client.post(url, data={'email': 'panda', 'password': '123456'})
        json_data = response.get_json()
        self.assertEqual(json_data['errorCode'], 'ILLEGAL_FORM')

    def test_register_with_password_not_matched(self):
        response = self.client.post(
            url_for('auth.register'),
            data={
                'nickname': 'panda',
                'email': '666@gmail.com',
                'password': '123456',  # 两次输入的密码不一致
                'password2': '234567'
            }
        )
        json_data = response.get_json()
        self.assertEqual(json_data['errorCode'], 'ILLEGAL_FORM')

    def test_register_with_existed_nickname(self):
        response = self.client.post(
            url_for('auth.register'),
            data={
                'nickname': 'dog',
                'email': 'tiger@gmail.com',
                'password': '123456',
                'password2': '123456'
            }
        )
        json_data = response.get_json()
        self.assertEqual(json_data['errorCode'], 'NICKNAME_ALREADY_USED')

    def test_register_with_existed_email(self):
        response = self.client.post(
            url_for('auth.register'),
            data={
                'nickname': 'tiger',
                'email': 'dog@gmail.com',
                'password': '123456',
                'password2': '123456'
            }
        )
        json_data = response.get_json()
        self.assertEqual(json_data['errorCode'], 'EMAIL_ALREADY_REGISTERED')

    def test_register(self):
        admin_email = current_app.config['ADMIN_EMAIL']
        response = self.client.post(
            url_for('auth.register'),
            data={
                'nickname': 'admin',
                'email': admin_email,
                'password': '123456',
                'password2': '123456'
            }
        )
        json_data = response.get_json()
        self.assertEqual(json_data['status'], 'OK')
        user = User.get_by_email(admin_email, enabled=True)
        self.assertFalse(user is None)
        self.assertEqual(user.role, UserRole.ADMINISTRATOR)

    def test_logout(self):
        response = self.client.post(
            url_for('auth.login'),
            data={'email': 'panda@gmail.com', 'password': '123456'}
        )
        json_data = response.get_json()
        self.assertEqual(json_data['status'], 'OK')

        response = self.client.post(
            url_for('auth.logout'),
            data={}
        )
        json_data = response.get_json()
        self.assertEqual(json_data['status'], 'OK')


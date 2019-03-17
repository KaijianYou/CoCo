import unittest
from unittest.mock import MagicMock, patch

from flask import url_for, current_app

from coco import create_app, db
from coco.models.user import User, UserRole
from coco.utils.testing_utils import create_user_data
from coco.utils.email_util import EmailUtil


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
        response = self.client.post(
            url,
            data={
                'email': 'panda@gmail.com',
                'password': '123456'
            }
        )
        json_data = response.get_json()
        self.assertTrue(json_data['success'])

    def test_login_with_wrong_password(self):
        url = url_for('auth.login')
        response = self.client.post(
            url,
            data={
                'email': 'panda@gmail.com',
                'password': '345987'
            }
        )
        json_data = response.get_json()
        self.assertEqual(json_data['errorCode'], 'WRONG_EMAIL_OR_PASSWORD')

    def test_login_with_invalid_form_value(self):
        url = url_for('auth.login')
        response = self.client.post(
            url,
            data={
                'email': 'panda',
                'password': '123456'
            }
        )
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
        self.assertTrue(json_data['success'])
        user = User.get_by_email(admin_email, deleted=False)
        self.assertFalse(user is None)
        self.assertEqual(user.role, UserRole.ADMINISTRATOR)

    def test_logout(self):
        # 登录
        response = self.client.post(
            url_for('auth.login'),
            data={
                'email': 'panda@gmail.com',
                'password': '123456'
            }
        )
        json_data = response.get_json()
        self.assertTrue(json_data['success'])

        response = self.client.post(
            url_for('auth.logout'),
            data={}
        )
        json_data = response.get_json()
        self.assertTrue(json_data['success'])

    def test_request_password_reset_after_login(self):
        # 登录
        response = self.client.post(
            url_for('auth.login'),
            data={
                'email': 'panda@gmail.com',
                'password': '123456'
            }
        )
        json_data = response.get_json()
        self.assertTrue(json_data['success'])

        response = self.client.post(
            url_for('auth.request_password_reset'),
            data={
                'email': 'panda@gmail.com'
            }
        )
        json_data = response.get_json()
        self.assertEqual(json_data['errorCode'], 'ALREADY_LOGIN')

    def test_request_password_reset_with_invalid_form_value(self):
        response = self.client.post(
            url_for('auth.request_password_reset'),
            data={}
        )
        json_data = response.get_json()
        self.assertEqual(json_data['errorCode'], 'ILLEGAL_FORM')

    def test_request_password_reset_with_unregistered_email(self):
        response = self.client.post(
            url_for('auth.request_password_reset'),
            data={
                'email': 'howtomake@love.com'
            }
        )
        json_data = response.get_json()
        self.assertEqual(json_data['errorCode'], 'EMAIL_NOT_REGISTERED')

    def test_request_password_reset(self):
        EmailUtil.send_password_reset_email = MagicMock(name='send_password_reset_email')
        # patch 会被调用到的方法，设置它们的返回值
        with patch.object(User, 'get_password_reset_token', return_value='I am a token'):
            response = self.client.post(
                url_for('auth.request_password_reset'),
                data={
                    'email': 'panda@gmail.com'
                }
            )
            json_data = response.get_json()
            self.assertTrue(json_data['success'])

            EmailUtil.send_password_reset_email.assert_called_once_with(
                ['panda@gmail.com'],
                'panda',
                'http://localhost/api/auth/reset-password/I%20am%20a%20token'
            )

    def test_verify_password_token_after_login(self):
        # 登录
        response = self.client.post(
            url_for('auth.login'),
            data={
                'email': 'panda@gmail.com',
                'password': '123456'
            }
        )
        json_data = response.get_json()
        self.assertTrue(json_data['success'])

        response = self.client.get(
            url_for('auth.verify_password_token', token='I am a token')
        )
        json_data = response.get_json()
        self.assertEqual(json_data['errorCode'], 'ALREADY_LOGIN')

    def test_verify_password_token(self):
        response = self.client.get(
            url_for('auth.verify_password_token', token='I am a token')
        )
        json_data = response.get_json()
        self.assertEqual(json_data['errorCode'], 'PASSWORD_RESET_TOKEN_INVALID')

    def test_reset_password_after_login(self):
        # 登录
        response = self.client.post(
            url_for('auth.login'),
            data={
                'email': 'panda@gmail.com',
                'password': '123456'
            }
        )
        json_data = response.get_json()
        self.assertTrue(json_data['success'])

        response = self.client.post(
            url_for('auth.reset_password', user_id=1)
        )
        json_data = response.get_json()
        self.assertEqual(json_data['errorCode'], 'ALREADY_LOGIN')

    def test_reset_password_with_invalid_form_value(self):
        response = self.client.post(
            url_for('auth.reset_password', user_id=1),
            data={
                'password': '123456789',
                'password2': '123456'
            }
        )
        json_data = response.get_json()
        self.assertEqual(json_data['errorCode'], 'ILLEGAL_FORM')

    def test_reset_password(self):
        response = self.client.post(
            url_for('auth.reset_password', user_id=1),
            data={
                'password': '123456789',
                'password2': '123456789'
            }
        )
        json_data = response.get_json()
        self.assertTrue(json_data['success'])
        user = User.get_by_id(1, deleted=False)
        self.assertTrue(user.verify_password('123456789'))

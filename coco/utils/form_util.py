from wtforms.validators import Regexp


class PasswordRequired:
    def __init__(self):
        self.password_format = r'^[A-Za-z0-9_@#]{6,32}'
        self.message = '密码长度必须在6到12个字符之间，且只能出现数字、英文字母以及 _ @ # 等字符'

    def __call__(self, form, field):
        Regexp(self.password_format).__call__(form, field, self.message)


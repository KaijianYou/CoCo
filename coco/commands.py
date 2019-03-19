import sys
import os
from getpass import getpass

import click
from flask.helpers import get_env

from coco import create_app
from coco.utils.validation_util import validate_password, ValidationError, validate_email


BASE_DIR = os.path.abspath(os.path.dirname(__file__))
TEST_PATH = os.path.join(BASE_DIR, 'tests')
COVERAGE_PATH = os.path.join(BASE_DIR, '.coverage')


"""
如果需要在 command 中使用 flask-sqlalchemy 查询或修改表数据，需要在 command 函数中调用如下语句：
    from flask.helpers import get_env
    app = create_app(get_env())
    app.app_context().push()
"""

@click.command()
def test(path=None):
    """调用方法：
    flask test
    flask test --path={path}

    例：只执行某个测试方法：
        flask test --path={file}::{test_class}::{test_method}
    """
    import pytest
    import coverage

    # 统计代码测试覆盖率
    COV = coverage.coverage(branch=True, include=f'{BASE_DIR}/*', omit=f'{BASE_DIR}/tests/*')
    COV.start()

    p = path or TEST_PATH
    rv = pytest.main([p, '--verbose', '-s'])

    COV.stop()
    COV.save()
    print('Coverage Summary:')
    COV.report()
    COV.html_report(directory=COVERAGE_PATH)
    print(f'HTML version: file://{COVERAGE_PATH}/index.html')
    COV.erase()

    exit(rv)


def stderr_print(message: str):
    print(message, file=sys.stderr)


@click.command()
def create_super_admin():
    """创建超级管理员
    调用命令：flask create-super-admin
    """
    from .models.auth_user import AuthUser, UserGroup

    app = create_app(get_env())
    app.app_context().push()

    username = None
    username_ok = False
    while not username_ok:
        username = input('用户名：').strip()
        if not username:
            continue
        if len(username) < 4 or len(username) > 32:
            stderr_print('用户名长度必须为 4 ~ 32 个字符！')
            continue
        user = AuthUser.get_by_username(username)
        if user:
            stderr_print('用户名已存在！')
            continue
        username_ok = True

    email = None
    email_ok = False
    while not email_ok:
        email = input('Email：').strip()
        if not email:
            continue
        try:
            validate_email(email)
        except ValidationError as err:
            stderr_print(err.message)
            continue
        else:
            email_ok = True

    password = None
    password_ok = False
    while not password_ok:
        password = getpass('密码：').strip()
        if not password:
            continue
        try:
            validate_password(password)
        except ValidationError as err:
            stderr_print(err.message)
            response = input('确定要使用这个密码吗? [y/N]: ')
            if response.lower() == 'y':
                password_ok = True
        else:
            password_ok = True

    password2 = getpass('确认密码：').strip()
    if password2 != password:
        stderr_print('密码不一致。')
        return
    AuthUser.create(
        username=username,
        email=email,
        password=password,
        group=UserGroup.Admin,
    )
    stderr_print('创建成功')



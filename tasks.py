import os

from invoke import task


AUTOAPP = 'autoapp.py'
CONFIG_ENV = os.environ.get('COCO_CONFIG_ENV', 'default')
FLASK_APP_ENV = f'FLASK_APP={AUTOAPP} FLASK_ENV={CONFIG_ENV}'
FLASK_APP_TEST_ENV = f'FLASK_APP={AUTOAPP} FLASK_ENV=test'


@task
def debug(ctx):
    """在 Debug 模式下启动应用
    使用：invoke debug
    """
    ctx.run(f'{FLASK_APP_ENV} FLASK_DEBUG=1 flask run', echo=True)


@task
def run(ctx):
    """在非 Debug 模式下启动应用
    使用：invoke run
    """
    ctx.run(f'{FLASK_APP_ENV} flask run', echo=True)


@task
def shell(ctx):
    """运行 shell
    使用：shell"""
    ctx.run(f'{FLASK_APP_ENV} flask shell', echo=True)


@task
def pip_update(ctx):
    """使用 Pipenv 更新依赖包
    使用：invoke pip-update
    """
    ctx.run('pipenv install', echo=True)


@task
def db_init(ctx):
    """创建数据库迁移
    使用：invoke db-init
    """
    ctx.run(f'{FLASK_APP_ENV} flask db init')


@task
def db_migrate(ctx):
    """创建数据库迁移脚本
    使用：invoke db-migrate
    """
    ctx.run(f'{FLASK_APP_ENV} flask db migrate')


@task
def db_upgrade(ctx):
    """引用数据迁移
    使用：invoke db-upgrade
    """
    ctx.run(f'{FLASK_APP_ENV} flask db upgrade')


@task
def db_downgrade(ctx):
    """回滚数据迁移
    使用：invoke db-downgrade
    """
    ctx.run(f'{FLASK_APP_ENV} flask db downgrade')


@task
def urls(ctx):
    """输出应用中所有注册的路由
    使用：invoke urls
    """
    ctx.run(f'{FLASK_APP_ENV} flask urls', echo=True)


@task
def test(ctx):
    """运行测试脚本
    使用：invoke test
    """
    ctx.run(f'{FLASK_APP_TEST_ENV} flask test', echo=True)


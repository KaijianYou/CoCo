from invoke import task


AUTOAPP = 'autoapp.py'
CONFIG_ENV = 'development'
PREREQUISITE = f'FLASK_APP={AUTOAPP} FLASK_ENV={CONFIG_ENV}'


@task
def debug(ctx):
    """运行：invoke debug"""
    ctx.run(f'{PREREQUISITE} flask run', echo=True)


@task
def pip_update(ctx):
    """运行：invoke pip-update"""
    ctx.run('pipenv install', echo=True)


@task
def db_init(ctx):
    """运行：invoke db-init"""
    ctx.run(f'{PREREQUISITE} flask db init')


@task
def db_migrate(ctx):
    """运行：invoke db-migrate"""
    ctx.run(f'{PREREQUISITE} flask db migrate')


@task
def db_upgrade(ctx):
    """运行：invoke db-upgrade"""
    ctx.run(f'{PREREQUISITE} flask db upgrade')


@task
def db_downgrade(ctx):
    """运行：invoke db-downgrade"""
    ctx.run(f'{PREREQUISITE} flask db downgrade')


@task
def test(ctx):
    """运行：invoke test"""
    ctx.run(f'FLASK_APP={AUTOAPP} flask test')


@task
def urls(ctx):
    """运行：invoke urls"""
    ctx.run(f'FLASK_APP={AUTOAPP} flask urls')

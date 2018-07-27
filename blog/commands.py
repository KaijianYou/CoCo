import os
from functools import wraps

from flask import current_app
from flask.cli import with_appcontext
import click


BASE_DIR = os.path.abspath(os.path.dirname(__file__))
TEST_PATH = os.path.join(BASE_DIR, 'tests')
COVERAGE_PATH = os.path.join(BASE_DIR, 'coverage')
AUTOAPP = 'autoapp.py'
CONFIG_ENV = os.environ.get('COCO_CONFIG_ENV', 'default')


def set_env(app=AUTOAPP, env=CONFIG_ENV):
    os.putenv('FLASK_APP', app)
    os.putenv('FLASK_ENV', env)


@click.command()
def debug():
    set_env()
    os.putenv('FLASK_DEBUG', '1')
    os.system('flask run')


@click.command()
def test():
    import pytest
    import coverage

    set_env(env='test')

    # 统计代码测试覆盖率
    COV = coverage.coverage(branch=True, include=f'{BASE_DIR}/*')
    COV.start()

    rv = pytest.main([TEST_PATH, '--verbose', '-s'])

    COV.stop()
    COV.save()
    print('Coverage Summary:')
    COV.report()
    COV.html_report(directory=COVERAGE_PATH)
    print(f'HTML version: file://{COVERAGE_PATH}/index.html')
    COV.erase()

    exit(rv)


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
def shell():
    set_env()
    os.system('flask shell')


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


@click.command()
@with_appcontext
def urls():
    set_env()

    rows = []
    column_headers = ('Rule', 'Endpoint', 'Arguments')

    rules = current_app.url_map.iter_rules()
    for rule in rules:
        rows.append((rule.rule, rule.endpoint, rule.arguments))

    row_template = ''
    table_width = 0

    max_rule_length = max(len(row[0]) for row in rows)
    row_template += f'{{:{max_rule_length}}}'
    table_width += max_rule_length

    max_endpoint_length = max(len(str(row[1])) for row in rows)
    row_template += f'    {{:{max_endpoint_length}}}'
    table_width += 4 + max_endpoint_length

    max_arguments_length = max(len(str(row[2])) for row in rows)
    row_template += f'    {{:{max_arguments_length}}}'
    table_width += 4 + max_arguments_length

    click.echo(row_template.format(*column_headers))
    click.echo('-' * table_width)
    for row in rows:
        rule, endpoint, arguments = row[0], row[1], ','.join(list(row[2]))
        click.echo(row_template.format(rule, endpoint, arguments))

import os

import click


PARENT_NAME = os.path.dirname(__file__)
PARENT_PATH = os.path.abspath(PARENT_NAME)
TEST_PATH = os.path.join(PARENT_PATH, 'tests')
COVERAGE_PATH = os.path.join(PARENT_NAME, 'coverage')


@click.command()
def test(coverage=False):
    import pytest
    import coverage

    # 统计代码测试覆盖率
    COV = coverage.coverage(branch=True, include=f'{PARENT_NAME}/*')
    COV.start()

    rv = pytest.main([TEST_PATH, '--verbose'])

    COV.stop()
    COV.save()
    print('Coverage Summary:')
    COV.report()
    COV.html_report(directory=COVERAGE_PATH)
    print(f'HTML version: file://{COVERAGE_PATH}/index.html')
    COV.erase()

    exit(rv)

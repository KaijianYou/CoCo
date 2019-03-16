import os

import click


BASE_DIR = os.path.abspath(os.path.dirname(__file__))
TEST_PATH = os.path.join(BASE_DIR, 'tests')
COVERAGE_PATH = os.path.join(BASE_DIR, '.coverage')


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


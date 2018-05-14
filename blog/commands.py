import os

import click


PARENT_NAME = os.path.dirname(__file__)
PARENT_PATH = os.path.abspath(PARENT_NAME)
TEST_PATH = os.path.join(PARENT_PATH, 'tests')


COV = None
if os.environ.get('flask_coverage', None):
    import coverage
    COV = coverage.coverage(branch=True, include=f'{PARENT_NAME}/*')
    COV.start()


@click.command()
def test():
    import pytest
    rv = pytest.main([TEST_PATH, '--verbose'])
    exit(rv)



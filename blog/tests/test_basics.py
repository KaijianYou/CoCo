import unittest

from blog.app import create_app, db


class TestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('test')
        self.app_context = self.app.test_request_context()
        self.app_context.push()
        self.client = self.app.test_client()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_production_config(self):
        app = create_app('production')
        self.assertEqual(app.config['ENV'], 'production')
        self.assertFalse(app.config['DEBUG'])

    def test_development_config(self):
        app = create_app('development')
        self.assertEqual(app.config['ENV'], 'development')
        self.assertTrue(app.config['DEBUG'])

    def test_test_config(self):
        app = create_app('test')
        self.assertEqual(app.config['ENV'], 'test')
        self.assertTrue(app.config['TESTING'])

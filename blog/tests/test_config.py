import unittest

from blog.app import create_app


class TestCase(unittest.TestCase):
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

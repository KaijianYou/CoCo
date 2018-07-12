import unittest
from datetime import datetime

from flask import url_for

from blog.app import create_app, db
from blog.utils import generate_fake_data
from blog.models.article import Article
from blog.models.user import User
from blog.models.category import Category
from blog.models.comment import Comment
from blog.models.tag import Tag
from blog.models.article_tag import article_tag


class TestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('test')
        self.app_context = self.app.test_request_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client(use_cookies=True)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_search_articles_by_keyword(self):
        url = url_for('public.search_articles_by_keyword')
        response = self.client.get(url)
        json_data = response.get_json()
        self.assertEqual(json_data['errorCode'], 'QUERY_WORD_NOT_FOUND')

        response = self.client.get(f'{url}?query=python')
        json_data = response.get_json()
        self.assertEqual(json_data['status'], 'OK')
        self.assertEqual(json_data['data'], {})

    def test_category_list(self):
        generate_fake_data(Category, seed=1, total=1)
        url = url_for('public.category_list')
        response = self.client.get(url)
        json_data = response.get_json()
        categories = json_data['data']['categories']
        self.assertEqual(len(categories), 1)
        self.assertEqual(categories[0]['name'], 'center')

    def test_tag_list(self):
        generate_fake_data(Tag, seed=1, total=3)
        url = url_for('public.tag_list')
        response = self.client.get(url)
        json_data = response.get_json()
        tags = json_data['data']['tags']
        self.assertEqual(len(tags), 3)
        self.assertEqual(tags[0]['name'], 'center')
        self.assertEqual(tags[1]['name'], 'outside')
        self.assertEqual(tags[2]['name'], 'throw')

    def test_archive(self):
        generate_fake_data(User, seed=1, total=4)
        generate_fake_data(Tag, seed=1, total=5)
        generate_fake_data(Category, seed=1, total=2)
        generate_fake_data(Article, seed=1, total=3)
        url = url_for('public.archive')
        response = self.client.get(url)
        json_data = response.get_json()
        now = datetime.now()
        date_str = f'{now.year}年{now.month}月'
        self.assertEqual(len(json_data['data']['archive'][date_str]), 3)

    def test_article_detail(self):
        generate_fake_data(User, seed=1, total=1)
        generate_fake_data(Tag, seed=1, total=1)
        generate_fake_data(Category, seed=1, total=1)
        generate_fake_data(Article, seed=1, total=1)
        url = url_for('public.article_detail', article_id=1)
        response = self.client.get(url)
        json_data = response.get_json()
        articles = Article.query_all()
        article = articles[0]
        result = json_data['data']['article']
        self.assertEqual(result['id'], article.id)

    def test_article_list(self):
        generate_fake_data(User, seed=1, total=4)
        generate_fake_data(Tag, seed=1, total=5)
        generate_fake_data(Category, seed=1, total=2)
        generate_fake_data(Article, seed=1, total=3)
        articles = Article.query_all()
        article_ids_set = {article.id for article in articles}

        url = url_for('public.article_list')
        response = self.client.get(url)
        json_data = response.get_json()
        result_ids_set = {r['id'] for r in json_data['data']['articles']}

        self.assertEqual(article_ids_set, result_ids_set)

    def test_article_list_by_category_id(self):
        generate_fake_data(User, seed=1, total=4)
        generate_fake_data(Tag, seed=1, total=5)
        generate_fake_data(Category, seed=1, total=2)
        generate_fake_data(Article, seed=1, total=3)
        articles = Article.query.filter_by(category_id=2).all()
        article_ids_set = {article.id for article in articles}

        url = url_for('public.article_list_by_category_id', category_id=2)
        response = self.client.get(url)
        json_data = response.get_json()
        result_ids_set = {r['id'] for r in json_data['data']['articles']}

        self.assertEqual(article_ids_set, result_ids_set)

    # def test_article_list_by_tag_id(self):
    #     generate_fake_data(User, seed=1, total=4)
        # generate_fake_data(Tag, seed=1, total=5)
        # generate_fake_data(Category, seed=1, total=2)
        # generate_fake_data(Article, seed=1, total=3)
        # article_ids = article_tag.query.filter_by(tag_id=2).all()
        # article_ids_set = {article_id for article_id in article_ids}
        #
        # url = url_for('public.article_list_by_tag_id', tag_id=2)
        # response = self.client.get(url)
        # json_data = response.get_json()
        # result_ids_set = {r['id'] for r in json_data['data']['articles']}
        #
        # self.assertEqual(article_ids_set, result_ids_set)

    def test_comment_article(self):
        user = User.create(nickname='panda', email='panda@gmail.com', password='123456')
        url = url_for('auth.login')
        response = self.client.post(url, data={'email': 'panda@gmail.com', 'password': '123456'})
        json_data = response.get_json()
        self.assertEqual(json_data['status'], 'OK')

        generate_fake_data(User, seed=1, total=1)
        generate_fake_data(Tag, seed=1, total=1)
        generate_fake_data(Category, seed=1, total=1)
        generate_fake_data(Article, seed=1, total=1)
        comment_body = '666' * 100
        url = url_for('public.comment_article', article_id=1)
        response = self.client.post(
            url,
            data={
                'body': comment_body
            }
        )
        json_data = response.get_json()
        self.assertEqual(json_data['errorCode'], 'ILLEGAL_FORM')

        comment_body = '666'
        url = url_for('public.comment_article', article_id=1)
        response = self.client.post(
            url,
            data={
                'body': comment_body
            }
        )
        json_data = response.get_json()
        self.assertEqual(json_data['status'], 'OK')

        comment = Comment.query_by_id(1)
        self.assertEqual(comment.body_text, '666')
        self.assertEqual(comment.article_id, 1)
        self.assertEqual(comment.author_id, user.id)

    def test_comment_list_by_article_id(self):
        generate_fake_data(User, seed=1, total=4)
        generate_fake_data(Tag, seed=1, total=5)
        generate_fake_data(Category, seed=1, total=2)
        generate_fake_data(Article, seed=1, total=3)
        generate_fake_data(Comment, seed=1, total=10)
        comments = Comment.query.filter_by(article_id=2).all()
        comments_ids_set = {comment.id for comment in comments}

        url = url_for('public.comment_list_by_article_id', article_id=2)
        response = self.client.get(url)
        json_data = response.get_json()
        result_ids_set = {r['id'] for r in json_data['data']['comments']}

        self.assertEqual(comments_ids_set, result_ids_set)


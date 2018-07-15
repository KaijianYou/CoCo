import unittest
from datetime import datetime

from flask import url_for

from blog.app import create_app, db
from blog.models.article import Article
from blog.models.user import User, UserRole
from blog.models.category import Category
from blog.models.comment import Comment


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

    def create_fake_data(self):
        user1 = User.create(
            nickname='panda',
            email='panda@gmail.com',
            password='123456',
            role=UserRole.ADMINISTRATOR
        )
        user2 = User.create(nickname='lori', email='lori@gmail.com', password='000000')
        category1 = Category.create(name='杂谈')
        category2 = Category.create(name='计算机')
        Article.create(
            title='WebGL制作游戏',
            body_text='',
            tags='好玩,程序员',
            author_id=user1.id,
            category_id=category2.id,
            utc_created=datetime(2018, 1, 23)
        )
        Article.create(
            title='找工作',
            body_text='',
            tags='程序员,技术,招聘',
            author_id=user2.id,
            category_id=category2.id,
            utc_created=datetime(2018, 8, 1)
        )
        Article.create(
            title='网速慢',
            body_text='',
            tags='网络,技术,交易',
            author_id=user1.id,
            category_id=category1.id,
            utc_created=datetime(2017, 5, 3)
        )
        Comment.create(body='多面几家试试', author_id=1, article_id=2)
        Comment.create(body='我家的也很慢', author_id=2, article_id=3)
        Comment.create(body='可以学习three.js', author_id=2, article_id=1)
        Comment.create(body='给我一份简历', author_id=1, article_id=2)

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
        self.create_fake_data()
        response = self.client.get(url_for('public.category_list'))
        json_data = response.get_json()
        categories = json_data['data']['categories']
        self.assertEqual(len(categories), 2)
        self.assertEqual(categories[0]['name'], '杂谈')
        self.assertEqual(categories[1]['name'], '计算机')

    def test_tag_list(self):
        self.create_fake_data()
        response = self.client.get(url_for('public.tag_list'))
        json_data = response.get_json()
        tags = json_data['data']['tags']
        self.assertEqual(set(tags), {'好玩', '程序员', '技术', '招聘', '网络', '交易'})

    def test_archive(self):
        self.create_fake_data()
        response = self.client.get(url_for('public.archive'))
        json_data = response.get_json()
        self.assertEqual(json_data['data']['archive']['2018年1月'][0]['title'], 'WebGL制作游戏')
        self.assertEqual(json_data['data']['archive']['2018年8月'][0]['title'], '找工作')
        self.assertEqual(json_data['data']['archive']['2017年5月'][0]['title'], '网速慢')

    def test_article_detail(self):
        self.create_fake_data()
        response = self.client.get(url_for('public.article_detail', article_id=1))
        json_data = response.get_json()
        result = json_data['data']['article']
        self.assertEqual(result['id'], 1)
        self.assertEqual(result['viewCount'], 1)
        self.assertEqual(result['title'], 'WebGL制作游戏')
        self.assertEqual(result['tags'], ['好玩', '程序员'])
        self.assertEqual(result['category'], '计算机')
        self.assertEqual(result['author'], 'panda')
#
    def test_article_list(self):
        self.create_fake_data()
        response = self.client.get(url_for('public.article_list'))
        json_data = response.get_json()
        self.assertEqual(len(json_data['data']['articles']), 3)

    def test_article_list_by_category_id(self):
        self.create_fake_data()
        response = self.client.get(url_for('public.article_list_by_category_id', category_id=2))
        json_data = response.get_json()
        articles = json_data['data']['articles']
        self.assertEqual(len(articles), 2)
        self.assertEqual(articles[0]['title'], '找工作')
        self.assertEqual(articles[1]['title'], 'WebGL制作游戏')

    def test_article_list_by_tag(self):
        self.create_fake_data()
        response = self.client.get(url_for('public.article_list_by_tag', tag='技术'))
        json_data = response.get_json()
        articles = json_data['data']['articles']
        self.assertEqual(len(articles), 2)
        self.assertEqual(articles[0]['title'], '网速慢')
        self.assertEqual(articles[1]['title'], '找工作')

    def test_comment_list_by_article_id(self):
        self.create_fake_data()
        response = self.client.get(url_for('public.comment_list_by_article_id', article_id=2))
        json_data = response.get_json()
        comments = json_data['data']['comments']
        self.assertEqual(len(comments), 2)
        self.assertEqual(comments[0]['body'], '给我一份简历')
        self.assertEqual(comments[1]['body'], '多面几家试试')

    def test_publish_article(self):
        self.create_fake_data()
        response = self.client.post(
            url_for('auth.login'),
            data={
                'email': 'panda@gmail.com',
                'password': '123456'
            }
        )
        json_data = response.get_json()
        self.assertEqual(json_data['status'], 'OK')

        response = self.client.post(
            url_for('public.publish_article'),
            data={
                'title': 'Flask框架初探',
                'body': 'Flask框架是一个用Python实现的微框架。...',
                'category_id': 1,
                'tags': 'Python,Flask,Web'
            }
        )
        json_data = response.get_json()
        self.assertEqual(json_data['status'], 'OK')

        article = Article.query.filter_by(title='Flask框架初探', is_enable=True).first()
        self.assertEqual(article.body_text, 'Flask框架是一个用Python实现的微框架。...')
        self.assertEqual(article.category_id, 1)
        self.assertEqual(article.tags, 'Python,Flask,Web')

    def test_edit_article(self):
        self.create_fake_data()
        response = self.client.post(
            url_for('auth.login'),
            data={
                'email': 'panda@gmail.com',
                'password': '123456'
            }
        )
        json_data = response.get_json()
        self.assertEqual(json_data['status'], 'OK')

        response = self.client.post(
            url_for('public.edit_article', article_id=1),
            data={
                'title': '学习使用WebGL制作小游戏',
                'body': '...',
                'category_id': 2,
                'tags': '游戏,程序员,JavaScript'
            }
        )
        json_data = response.get_json()
        self.assertEqual(json_data['status'], 'OK')

        article = Article.query_by_id(1, is_enable=True)
        self.assertEqual(article.title, '学习使用WebGL制作小游戏')
        self.assertEqual(article.body_text, '...')
        self.assertEqual(article.category_id, 2)
        self.assertEqual(article.tags, '游戏,程序员,JavaScript')

    def test_review_comment(self):
        self.create_fake_data()
        response = self.client.post(
            url_for('auth.login'),
            data={
                'email': 'panda@gmail.com',
                'password': '123456'
            }
        )
        json_data = response.get_json()
        self.assertEqual(json_data['status'], 'OK')

        response = self.client.post(
            url_for('public.review_comment', comment_id=1),
            data={}
        )
        json_data = response.get_json()
        self.assertEqual(json_data['status'], 'OK')
        comment = Comment.query_by_id(1)
        self.assertEqual(comment.is_enable, False)

        response = self.client.post(
            url_for('public.review_comment', comment_id=1),
            data={}
        )
        json_data = response.get_json()
        self.assertEqual(json_data['status'], 'OK')
        comment = Comment.query_by_id(1)
        self.assertEqual(comment.is_enable, True)

    def test_publish_comment(self):
        self.create_fake_data()

        url = url_for('auth.login')
        response = self.client.post(url, data={'email': 'panda@gmail.com', 'password': '123456'})
        json_data = response.get_json()
        self.assertEqual(json_data['status'], 'OK')

        new_comment_body = '666' * 100
        response = self.client.post(
            url_for('public.publish_comment', article_id=1),
            data={
                'body': new_comment_body
            }
        )
        json_data = response.get_json()
        self.assertEqual(json_data['errorCode'], 'ILLEGAL_FORM')

        new_comment_body = '666'
        response = self.client.post(
            url_for('public.publish_comment', article_id=1),
            data={
                'body': new_comment_body
            }
        )
        json_data = response.get_json()
        self.assertEqual(json_data['status'], 'OK')

        comment = Comment.query\
            .filter_by(article_id=1, is_enable=True)\
            .order_by(Comment.id.desc())\
            .first()
        self.assertEqual(comment.body, new_comment_body)

    def test_modify_comment(self):
        self.create_fake_data()

        url = url_for('auth.login')
        response = self.client.post(url, data={'email': 'panda@gmail.com', 'password': '123456'})
        json_data = response.get_json()
        self.assertEqual(json_data['status'], 'OK')

        new_comment_body = '好好准备面试'
        response = self.client.post(
            url_for('public.modify_comment', comment_id=1),
            data={
                'body': new_comment_body
            }
        )
        json_data = response.get_json()
        self.assertEqual(json_data['status'], 'OK')
        comment = Comment.query_by_id(1, is_enable=True)
        self.assertEqual(comment.body, new_comment_body)


import unittest
from datetime import datetime

from flask import url_for

from blog.app import create_app, db
from blog.models.article import Article
from blog.models.comment import Comment
from blog.models.message import Message
from blog.utils.testing_utils import create_fake_data


class TestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('test')
        self.app_context = self.app.test_request_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client(use_cookies=True)
        create_fake_data()

    def tearDown(self):
        db.session.remove()
        self.app.elasticsearch.indices.delete('article')
        db.drop_all()
        self.app_context.pop()

    def test_search_articles(self):
        url = url_for('main.search_articles')
        response = self.client.get(url)
        json_data = response.get_json()
        self.assertEqual(json_data['errorCode'], 'QUERY_WORD_NOT_FOUND')

        import time
        time.sleep(1)

        keyword = '房子'
        response = self.client.get(f'{url}?query={keyword}')
        json_data = response.get_json()
        result = json_data['data']
        self.assertEqual(result['_meta']['total'], 2)
        article_slugs = [article['slug'] for article in result['articles']]
        self.assertEqual(article_slugs, ['12345678', '23456789'])

        keyword = '网速'
        response = self.client.get(f'{url}?query={keyword}')
        json_data = response.get_json()
        result = json_data['data']
        self.assertEqual(result['_meta']['total'], 1)
        article_slugs = [article['slug'] for article in result['articles']]
        self.assertEqual(article_slugs, ['23456789'])

        keyword = '程序员'
        response = self.client.get(f'{url}?query={keyword}')
        json_data = response.get_json()
        result = json_data['data']
        self.assertEqual(result['_meta']['total'], 2)
        article_slugs = [article['slug'] for article in result['articles']]
        self.assertEqual(article_slugs, ['12345678', '01234567'])

    def test_category_list(self):
        response = self.client.get(url_for('main.category_list'))
        json_data = response.get_json()
        categories = json_data['data']['categories']
        self.assertEqual(len(categories), 2)
        self.assertEqual(categories[0]['name'], '杂谈')
        self.assertEqual(categories[1]['name'], '计算机')

    def test_tag_list(self):
        response = self.client.get(url_for('main.tag_list'))
        json_data = response.get_json()
        tags = json_data['data']['tags']
        self.assertEqual(set(tags), {'好玩', '程序员', '技术', '招聘', '网络', '交易'})

    def test_archive(self):
        response = self.client.get(url_for('main.archive'))
        json_data = response.get_json()
        self.assertEqual(json_data['data']['archive']['2018年1月'][0]['title'], 'WebGL制作游戏')
        self.assertEqual(json_data['data']['archive']['2018年8月'][0]['title'], '找工作')
        self.assertEqual(json_data['data']['archive']['2017年5月'][0]['title'], '网速慢')

    def test_article_detail(self):
        response = self.client.get(url_for('main.article_detail', article_slug='01234567'))
        json_data = response.get_json()
        result = json_data['data']['article']
        self.assertEqual(result['slug'], '01234567')
        self.assertEqual(result['viewCount'], 1)
        self.assertEqual(result['title'], 'WebGL制作游戏')
        self.assertEqual(result['tags'], ['好玩', '程序员'])
        self.assertEqual(result['category'], '计算机')
        self.assertEqual(result['author'], 'panda')

    def test_article_list(self):
        response = self.client.get(url_for('main.article_list'))
        json_data = response.get_json()
        self.assertEqual(len(json_data['data']['articles']), 3)

    def test_article_list_by_category_id(self):
        response = self.client.get(url_for('main.article_list_by_category_id', category_id=2))
        json_data = response.get_json()
        articles = json_data['data']['articles']
        self.assertEqual(len(articles), 2)
        self.assertEqual(articles[0]['title'], '找工作')
        self.assertEqual(articles[1]['title'], 'WebGL制作游戏')

    def test_article_list_by_tag(self):
        response = self.client.get(url_for('main.article_list_by_tag', tag='技术'))
        json_data = response.get_json()
        articles = json_data['data']['articles']
        self.assertEqual(len(articles), 2)
        self.assertEqual(articles[0]['title'], '网速慢')
        self.assertEqual(articles[1]['title'], '找工作')

    def test_comment_list_by_article_slug(self):
        response = self.client.get(url_for('main.comment_list_by_article_slug', article_slug='12345678'))
        json_data = response.get_json()
        comments = json_data['data']['comments']
        self.assertEqual(len(comments), 2)
        self.assertEqual(comments[0]['body'], '给我一份简历')
        self.assertEqual(comments[1]['body'], '多面几家试试')

    def test_publish_article(self):
        response = self.client.post(
            url_for('auth.login'),
            data={
                'email': 'panda@gmail.com',
                'password': '123456'
            }
        )
        json_data = response.get_json()
        self.assertTrue(json_data['success'])

        response = self.client.post(
            url_for('main.publish_article'),
            data={
                'title': 'Flask框架初探',
                'body': 'Flask框架是一个用Python实现的微框架。...',
                'category_id': 1,
                'tags': 'Python,Flask,Web'
            }
        )
        json_data = response.get_json()
        self.assertTrue(json_data['success'])

        article = Article.get_by_title(title='Flask框架初探', enabled=True)
        self.assertEqual(article.body_text, 'Flask框架是一个用Python实现的微框架。...')
        self.assertEqual(article.category_id, 1)
        self.assertEqual(article.tags, 'Python,Flask,Web')

    def test_edit_article(self):
        response = self.client.post(
            url_for('auth.login'),
            data={
                'email': 'panda@gmail.com',
                'password': '123456'
            }
        )
        json_data = response.get_json()
        self.assertTrue(json_data['success'])

        response = self.client.post(
            url_for('main.edit_article', article_slug='01234567'),
            data={
                'title': '学习使用WebGL制作小游戏',
                'body': '...',
                'category_id': 2,
                'tags': '游戏,程序员,JavaScript'
            }
        )
        json_data = response.get_json()
        self.assertTrue(json_data['success'])

        article = Article.get_by_id(1, enabled=True)
        self.assertEqual(article.title, '学习使用WebGL制作小游戏')
        self.assertEqual(article.body_text, '...')
        self.assertEqual(article.category_id, 2)
        self.assertEqual(article.tags, '游戏,程序员,JavaScript')

    def test_review_comment(self):
        response = self.client.post(
            url_for('auth.login'),
            data={
                'email': 'panda@gmail.com',
                'password': '123456'
            }
        )
        json_data = response.get_json()
        self.assertTrue(json_data['success'])

        response = self.client.post(
            url_for('main.review_comment', comment_id=1),
            data={}
        )
        json_data = response.get_json()
        self.assertTrue(json_data['success'])
        comment = Comment.get_by_id(1)
        self.assertEqual(comment.enabled, False)

        response = self.client.post(
            url_for('main.review_comment', comment_id=1),
            data={}
        )
        json_data = response.get_json()
        self.assertTrue(json_data['success'])
        comment = Comment.get_by_id(1)
        self.assertEqual(comment.enabled, True)

    def test_publish_comment(self):
        url = url_for('auth.login')
        response = self.client.post(url, data={'email': 'panda@gmail.com', 'password': '123456'})
        json_data = response.get_json()
        self.assertTrue(json_data['success'])

        new_comment_body = '666' * 100
        response = self.client.post(
            url_for('main.publish_comment', article_slug='01234567'),
            data={
                'body': new_comment_body
            }
        )
        json_data = response.get_json()
        self.assertEqual(json_data['errorCode'], 'ILLEGAL_FORM')

        new_comment_body = '666'
        response = self.client.post(
            url_for('main.publish_comment', article_slug='01234567'),
            data={
                'body': new_comment_body
            }
        )
        json_data = response.get_json()
        self.assertTrue(json_data['success'])

        comment = Comment.get_latest_by_article_id(article_id=1, enabled=True)
        self.assertEqual(comment.body, new_comment_body)

    def test_modify_comment(self):
        url = url_for('auth.login')
        response = self.client.post(url, data={'email': 'panda@gmail.com', 'password': '123456'})
        json_data = response.get_json()
        self.assertTrue(json_data['success'])

        new_comment_body = '好好准备面试'
        response = self.client.post(
            url_for('main.modify_comment', comment_id=1),
            data={
                'body': new_comment_body
            }
        )
        json_data = response.get_json()
        self.assertTrue(json_data['success'])
        comment = Comment.get_by_id(1, enabled=True)
        self.assertEqual(comment.body, new_comment_body)

    def test_message_list(self):
        url = url_for('auth.login')
        response = self.client.post(url, data={'email': 'panda@gmail.com', 'password': '123456'})
        json_data = response.get_json()
        self.assertTrue(json_data['success'])

        url = url_for('main.message_list', filter_type='sent')
        response = self.client.get(url)
        json_data = response.get_json()
        message_ids = [message['id'] for message in json_data['data']['messages']]
        self.assertEqual([1], message_ids)

        url = url_for('main.message_list', filter_type='received')
        response = self.client.get(url)
        json_data = response.get_json()
        message_ids = [message['id'] for message in json_data['data']['messages']]
        self.assertEqual([2], message_ids)

    def test_send_message(self):
        url = url_for('auth.login')
        response = self.client.post(url, data={'email': 'panda@gmail.com', 'password': '123456'})
        json_data = response.get_json()
        self.assertTrue(json_data['success'])

        url = url_for('main.send_message', recipient_id=2)
        response = self.client.post(url,
            data={
                'body': '迪迦奥特曼'
            }
        )
        json_data = response.get_json()
        self.assertTrue(json_data['success'])
        message = Message.get_latest_by_sender_id(sender_id=1, enabled=True)
        self.assertTrue(message is not None)
        self.assertEqual(message.recipient_id, 2)

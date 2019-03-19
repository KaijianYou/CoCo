from datetime import datetime

from coco.models.auth_user import AuthUser, UserGroup
from coco.models.category import Category
from coco.models.article import Article
from coco.models.comment import Comment


def create_fake_data():
    user1 = AuthUser.create(
        nickname='panda',
        email='panda@gmail.com',
        password='123456',
        role=UserGroup.Admin
    )
    user2 = AuthUser.create(nickname='lori', email='lori@gmail.com', password='000000')
    category1 = Category.create(name='杂谈')
    category2 = Category.create(name='计算机')
    article1 = Article.create(
        title='WebGL制作游戏',
        body_text='WebGL 游戏 难',
        tags='好玩,程序员',
        author_id=user1.id,
        category_id=category2.id,
        created_time=datetime(2018, 1, 23)
    )
    article1.update(slug='01234567')
    article2 = Article.create(
        slug='12345678',
        title='找工作',
        body_text='工作，公司，面试，笔试，房子',
        tags='程序员,技术,招聘',
        author_id=user2.id,
        category_id=category2.id,
        created_time=datetime(2018, 8, 1)
    )
    article2.update(slug='12345678')
    article3 = Article.create(
        slug='23456789',
        title='网速慢',
        body_text='宽带，联通、电信，屏蔽，路由器 房子',
        tags='网络,技术,交易',
        author_id=user1.id,
        category_id=category1.id,
        created_time=datetime(2017, 5, 3)
    )
    article3.update(slug='23456789')
    Comment.create(body='多面几家试试', author_id=1, article_id=2)
    Comment.create(body='我家的也很慢', author_id=2, article_id=3)
    Comment.create(body='可以学习three.js', author_id=2, article_id=1)
    Comment.create(body='给我一份简历', author_id=1, article_id=2)


def create_user_data():
    AuthUser.create(nickname='panda', email='panda@gmail.com', password='123456')
    AuthUser.create(nickname='dog', email='dog@gmail.com', password='000000')


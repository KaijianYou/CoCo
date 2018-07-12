from collections import defaultdict
from datetime import timedelta

from flask import Blueprint, request, url_for
from flask_login import login_required, current_user

from .forms import CommentArticleForm
from blog.utils import generate_success_json, generate_error_json
from blog.models.category import Category
from blog.models.tag import Tag
from blog.models.article import Article
from blog.models.comment import Comment
from blog.const import Constant
from blog.errors import QUERY_WORD_NOT_FOUND, ARTICLE_NOT_EXISTS, \
    CATEGORY_NOT_EXISTS, TAG_NOT_EXISTS, ILLEGAL_FORM


blueprint = Blueprint('public', __name__)


@blueprint.route('/articles/search', methods=['GET'])
def search_articles_by_keyword():
    """TODO: 未完成"""
    keyword = request.args.get('query', None)
    if not keyword:
        return generate_error_json(QUERY_WORD_NOT_FOUND)
    result = {}
    return generate_success_json(result)


@blueprint.route('/categories/', methods=['GET'])
def category_list():
    categories = Category.query_all(is_enable=True)
    result = {
        'categories': [category.to_json() for category in categories]
    }
    return generate_success_json(result)


@blueprint.route('/tags/', methods=['GET'])
def tag_list():
    tags = Tag.query_all(is_enable=True)
    result = {
        'tags': [tag.to_json() for tag in tags]
    }
    return generate_success_json(result)


@blueprint.route('/archive', methods=['GET'])
def archive():
    articles = Article.query_all(is_enable=True, order='desc')
    archive_dict = defaultdict(list)
    for article in articles:
        article_create_datetime = article.utc_created + timedelta(hours=8)
        archive_date_str = f'{article_create_datetime.year}年'\
                           f'{article_create_datetime.month}月'
        article_json = {
            'title': article.title,
            'url': url_for(
                'public.article_detail',
                article_id=article.id,
                _external=True
            )
        }
        archive_dict[archive_date_str].append(article_json)
    result = {
        'archive': archive_dict
    }
    return generate_success_json(result)


@blueprint.route('/articles/<int:article_id>', methods=['GET'])
def article_detail(article_id):
    article = Article.query_by_id(article_id, is_enable=True)
    if not article:
        return generate_error_json(ARTICLE_NOT_EXISTS)

    result = {
        'article': article.to_json()
    }
    return generate_success_json(result)


@blueprint.route('/articles/', methods=['GET'])
def article_list():
    page = request.args.get('page', default=1, type=int)
    pagination = Article.paginate(
        is_enable=True,
        order='desc',
        page=page,
        per_page=Constant.ARTICLE_PAGE_SIZE
    )
    articles = pagination.items
    articles_json = [article.to_json() for article in articles]
    result = {
        'articles': articles_json
    }
    return generate_success_json(result)


@blueprint.route('/categories/<int:category_id>/articles/', methods=['GET'])
def article_list_by_category_id(category_id):
    category = Category.query_by_id(category_id, is_enable=True)
    if not category:
        return generate_error_json(CATEGORY_NOT_EXISTS)
    page = request.args.get('page', default=1, type=int)
    pagination = category.paginate_articles(
        order='desc', page=page, per_page=Constant.ARTICLE_PAGE_SIZE
    )
    articles = pagination.items
    result = {
        'articles': [article.to_json() for article in articles]
    }
    return generate_success_json(result)


@blueprint.route('/tags/<int:tag_id>/articles/', methods=['GET'])
def article_list_by_tag_id(tag_id):
    tag = Tag.query_by_id(tag_id, is_enable=True)
    if not tag:
        return generate_error_json(TAG_NOT_EXISTS)
    page = request.args.get('page', default=1, type=int)
    pagination = tag.paginate_articles(
        order='desc', page=page, per_page=Constant.ARTICLE_PAGE_SIZE
    )
    articles = pagination.items
    result = {
        'articles': [article.to_json() for article in articles]
    }
    return generate_success_json(result)


@blueprint.route('/articles/<int:article_id>/comment', methods=['POST'])
@login_required
def comment_article(article_id):
    article = Article.query_by_id(article_id, is_enable=True)
    if not article:
        return generate_error_json(ARTICLE_NOT_EXISTS)
    form = CommentArticleForm(meta={'csrf': False})
    if not form.validate_on_submit():
        return generate_error_json(ILLEGAL_FORM)

    Comment.create(body_text=form.body.data,
                   author_id=current_user.id,
                   article_id=article.id)
    return generate_success_json()


@blueprint.route('/articles/<int:article_id>/comments', methods=['GET'])
def comment_list_by_article_id(article_id):
    article = Article.query_by_id(article_id, is_enable=True)
    if not article:
        return generate_error_json(ARTICLE_NOT_EXISTS)
    page = request.args.get('page', default=1, type=int)
    pagination = article.paginate_comments(
        order='desc', page=page, per_page=Constant.COMMENT_PAGE_SIZE
    )
    comments = pagination.items
    result = {
        'comments': [comment.to_json() for comment in comments]
    }
    return generate_success_json(result)


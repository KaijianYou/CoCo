from collections import defaultdict
from datetime import timedelta

from flask import Blueprint, request, url_for
from flask_login import login_required, current_user

from .forms import CommentDetailForm, ArticleDetailForm
from blog.utils import generate_success_json, generate_error_json, permission_required
from blog.models.category import Category
from blog.models.user import UserPermission
from blog.models.article import Article
from blog.models.comment import Comment
from blog.const import Constant
from blog import errors


blueprint = Blueprint('public', __name__)


@blueprint.route('/articles/search', methods=['GET'])
def search_articles_by_keyword():
    """TODO: 根据关键词查找文章"""
    keyword = request.args.get('query', None)
    if not keyword:
        return generate_error_json(errors.QUERY_WORD_NOT_FOUND)
    result = {}
    return generate_success_json(result)


@blueprint.route('/categories/', methods=['GET'])
def category_list():
    categories = Category.list(enabled=True)
    result = {
        'categories': [category.to_json() for category in categories]
    }
    return generate_success_json(result)


@blueprint.route('/tags/', methods=['GET'])
def tag_list():
    tags_list = Article.list_tags(enabled=True)
    tags_set = set()
    for t in tags_list:
        tag_list = t[0].split(',') if t[0] else []
        for tag in tag_list:
            tags_set.add(tag)
    result = {
        'tags': list(tags_set)
    }
    return generate_success_json(result)


@blueprint.route('/archive', methods=['GET'])
def archive():
    articles = Article.list(enabled=True, order='desc')
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
    article = Article.get_by_id(article_id, enabled=True)
    if not article:
        return generate_error_json(errors.ARTICLE_NOT_EXISTS)

    view_count = article.view_count + 1
    article.update(view_count=view_count)
    result = {
        'article': article.to_json()
    }
    return generate_success_json(result)


@blueprint.route('/articles/', methods=['GET'])
def article_list():
    page = request.args.get('page', default=1, type=int)
    pagination = Article.paginate(
        enabled=True,
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
    category = Category.get_by_id(category_id, enabled=True)
    if not category:
        return generate_error_json(errors.CATEGORY_NOT_EXISTS)
    page = request.args.get('page', default=1, type=int)
    pagination = category.paginate_articles(
        order='desc', page=page, per_page=Constant.ARTICLE_PAGE_SIZE
    )
    articles = pagination.items
    result = {
        'articles': [article.to_json() for article in articles]
    }
    return generate_success_json(result)


@blueprint.route('/tags/<string:tag>/articles/', methods=['GET'])
def article_list_by_tag(tag):
    page = request.args.get('page', default=1, type=int)
    pagination = Article.paginate_by_tag(
        tag,
        order='desc',
        page=page,
        per_page=Constant.ARTICLE_PAGE_SIZE
    )
    articles = pagination.items
    result = {
        'articles': [article.to_json() for article in articles]
    }
    return generate_success_json(result)


@blueprint.route('/articles/<int:article_id>/comments', methods=['GET'])
def comment_list_by_article_id(article_id):
    article = Article.get_by_id(article_id, enabled=True)
    if not article:
        return generate_error_json(errors.ARTICLE_NOT_EXISTS)
    page = request.args.get('page', default=1, type=int)
    pagination = article.paginate_comments(
        order='desc', page=page, per_page=Constant.COMMENT_PAGE_SIZE
    )
    comments = pagination.items
    result = {
        'comments': [comment.to_json() for comment in comments]
    }
    return generate_success_json(result)


@blueprint.route('/articles/publish', methods=['POST'])
@login_required
@permission_required(UserPermission.PUBLISH_ARTICLE)
def publish_article():
    """发表文章"""
    form = ArticleDetailForm(meta={'csrf': False})
    if not form.validate_on_submit():
        return generate_error_json(errors.ILLEGAL_FORM)

    Article.create(
        title=form.title.data,
        body_text=form.body.data,
        category_id=form.category_id.data,
        author_id=current_user.id,
        tags=form.tags.data
    )
    return generate_success_json()


@blueprint.route('/articles/<int:article_id>/edit', methods=['POST'])
@login_required
@permission_required(UserPermission.PUBLISH_ARTICLE)
def edit_article(article_id):
    """编辑文章"""
    form = ArticleDetailForm(meta={'csrf': False})
    if not form.validate_on_submit():
        return generate_error_json(errors.ILLEGAL_FORM)
    article = Article.get_by_id(article_id, enabled=True)
    if not article:
        return generate_error_json(errors.ARTICLE_NOT_EXISTS)
    article.update(
        title=form.title.data,
        body_text=form.body.data,
        category_id=form.category_id.data,
        tags=form.tags.data
    )
    return generate_success_json()


@blueprint.route('/comments/<int:comment_id>/change-state', methods=['POST'])
@login_required
@permission_required(UserPermission.REVIEW_COMMENT)
def review_comment(comment_id):
    """管理评论"""
    comment = Comment.get_by_id(comment_id)
    if not comment:
        return generate_error_json(errors.COMMENT_NOT_EXISTS)
    enabled = not comment.enabled
    comment.update(enabled=enabled)
    return generate_success_json()


@blueprint.route('/articles/<int:article_id>/comment', methods=['POST'])
@login_required
@permission_required(UserPermission.COMMENT)
def publish_comment(article_id):
    """发表评论"""
    article = Article.get_by_id(article_id, enabled=True)
    if not article:
        return generate_error_json(errors.ARTICLE_NOT_EXISTS)
    form = CommentDetailForm(meta={'csrf': False})
    if not form.validate_on_submit():
        return generate_error_json(errors.ILLEGAL_FORM)
    Comment.create(
        body=form.body.data,
        author_id=current_user.id,
        article_id=article.id
    )
    return generate_success_json()


@blueprint.route('/comments/<int:comment_id>/modify', methods=['POST'])
@login_required
@permission_required(UserPermission.COMMENT)
def modify_comment(comment_id):
    """修改评论"""
    comment = Comment.get_by_id(comment_id, enabled=True)
    if not comment:
        return generate_error_json(errors.COMMENT_NOT_EXISTS)
    if comment.author_id != current_user.id:
        return generate_error_json(errors.USER_PERMISSION_DENIED)
    form = CommentDetailForm(meta={'csrf': False})
    if not form.validate_on_submit():
        return generate_error_json(errors.ILLEGAL_FORM)
    comment.update(body=form.body.data)
    return generate_success_json()


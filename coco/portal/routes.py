from collections import defaultdict
from datetime import datetime, timedelta

from flask import Blueprint, request, url_for
from flask_login import login_required, current_user

from coco.utils.json_util import gen_success_json, gen_error_json
from coco.utils.other_utils import permission_required, page_meta_data
from coco.models.category import Category
from coco.models.user import User, UserPermission
from coco.models.article import Article
from coco.models.comment import Comment
from coco.models.message import Message
from coco.const import Constant
from coco import errors
from .forms import CommentDetailForm, ArticleDetailForm, MessageForm


blueprint = Blueprint('main', __name__)


@blueprint.route('/articles/search', methods=['GET'])
def search_articles():
    keyword = request.args.get('query', None)
    if not keyword:
        return gen_error_json(errors.QUERY_WORD_NOT_FOUND)
    page = request.args.get('page', 1, type=int)
    page_size = Constant.ARTICLE_PAGE_SIZE
    articles, total = Article.search(keyword, page, page_size)
    articles_json = [article.to_dict() for article in articles]
    data = {
        'articles': articles_json
    }
    data.update(page_meta_data(page, page_size, total))
    return gen_success_json(data)


@blueprint.route('/categories/', methods=['GET'])
def category_list():
    categories = Category.list_all(deleted=False)
    data = {
        'categories': [category.to_dict() for category in categories]
    }
    return gen_success_json(data)


@blueprint.route('/tags/', methods=['GET'])
def tag_list():
    tags_list = Article.list_tags(deleted=False)
    tags_set = set()
    for t in tags_list:
        tag_list = t[0].split(',') if t[0] else []
        for tag in tag_list:
            tags_set.add(tag)
    data = {
        'tags': list(tags_set)
    }
    return gen_success_json(data)


@blueprint.route('/archive', methods=['GET'])
def archive():
    articles = Article.list_all(deleted=False, order='desc')
    archive_dict = defaultdict(list)
    for article in articles:
        article_create_datetime = article.created_time + timedelta(hours=8)
        archive_date_str = (f'{article_create_datetime.year}年'
                            f'{article_create_datetime.month}月')
        article_json = {
            'title': article.title,
            'url': url_for(
                'main.article_detail',
                article_slug=article.slug,
                _external=True
            )
        }
        archive_dict[archive_date_str].append(article_json)
    data = {
        'archive': archive_dict
    }
    return gen_success_json(data)


@blueprint.route('/articles/<string:article_slug>', methods=['GET'])
def article_detail(article_slug):
    article = Article.get_by_slug(article_slug, deleted=False)
    if not article:
        return gen_error_json(errors.ARTICLE_NOT_EXISTS)

    view_count = article.view_count + 1
    article.update(view_count=view_count)
    data = {
        'article': article.to_dict()
    }
    return gen_success_json(data)


@blueprint.route('/articles/', methods=['GET'])
def article_list():
    page = request.args.get('page', default=1, type=int)
    page_size = Constant.ARTICLE_PAGE_SIZE
    pagination = Article.paginate(
        deleted=False,
        order='desc',
        page=page,
        per_page=page_size
    )
    articles = pagination.items
    articles_json = [article.to_dict() for article in articles]
    data = {
        'articles': articles_json
    }
    data.update(page_meta_data(page, page_size, pagination.total))
    return gen_success_json(data)


@blueprint.route('/categories/<int:category_id>/articles/', methods=['GET'])
def article_list_by_category_id(category_id):
    category = Category.get_by_id(category_id, deleted=False)
    if not category:
        return gen_error_json(errors.CATEGORY_NOT_EXISTS)
    page = request.args.get('page', default=1, type=int)
    page_size = Constant.ARTICLE_PAGE_SIZE
    pagination = category.paginate_articles(
        order='desc', page=page, per_page=page_size
    )
    articles = pagination.items
    data = {
        'articles': [article.to_dict() for article in articles]
    }
    data.update(page_meta_data(page, page_size, pagination.total))
    return gen_success_json(data)


@blueprint.route('/tags/<string:tag>/articles/', methods=['GET'])
def article_list_by_tag(tag):
    page = request.args.get('page', default=1, type=int)
    page_size = Constant.ARTICLE_PAGE_SIZE
    pagination = Article.paginate_by_tag(
        tag,
        order='desc',
        page=page,
        per_page=page_size
    )
    articles = pagination.items
    data = {
        'articles': [article.to_dict() for article in articles]
    }
    data.update(page_meta_data(page, page_size, pagination.total))
    return gen_success_json(data)


@blueprint.route('/articles/<string:article_slug>/comments', methods=['GET'])
def comment_list_by_article_slug(article_slug):
    article = Article.get_by_slug(article_slug, deleted=False)
    if not article:
        return gen_error_json(errors.ARTICLE_NOT_EXISTS)
    page = request.args.get('page', default=1, type=int)
    page_size = Constant.COMMENT_PAGE_SIZE
    pagination = article.paginate_comments(
        order='desc', page=page, per_page=page_size
    )
    comments = pagination.items
    data = {
        'comments': [comment.to_dict() for comment in comments]
    }
    data.update(page_meta_data(page, page_size, pagination.total))
    return gen_success_json(data)


@blueprint.route('/articles/publish', methods=['POST'])
@login_required
@permission_required(UserPermission.PUBLISH_ARTICLE)
def publish_article():
    """发表文章"""
    form = ArticleDetailForm(meta={'csrf': False})
    if not form.validate_on_submit():
        return gen_error_json(errors.ILLEGAL_FORM)

    Article.create(
        title=form.title.data,
        body_text=form.body.data,
        category_id=form.category_id.data,
        author_id=current_user.id,
        tags=form.tags.data
    )
    return gen_success_json()


@blueprint.route('/articles/<string:article_slug>/edit', methods=['POST'])
@login_required
@permission_required(UserPermission.PUBLISH_ARTICLE)
def edit_article(article_slug):
    """编辑文章"""
    form = ArticleDetailForm(meta={'csrf': False})
    if not form.validate_on_submit():
        return gen_error_json(errors.ILLEGAL_FORM)
    article = Article.get_by_slug(article_slug, deleted=False)
    if not article:
        return gen_error_json(errors.ARTICLE_NOT_EXISTS)
    article.update(
        title=form.title.data,
        body_text=form.body.data,
        category_id=form.category_id.data,
        tags=form.tags.data
    )
    return gen_success_json()


@blueprint.route('/comments/<int:comment_id>/change-state', methods=['POST'])
@login_required
@permission_required(UserPermission.REVIEW_COMMENT)
def review_comment(comment_id):
    """管理评论"""
    comment = Comment.get_by_id(comment_id)
    if not comment:
        return gen_error_json(errors.COMMENT_NOT_EXISTS)
    deleted = not comment.deleted
    comment.update(deleted=deleted)
    return gen_success_json()


@blueprint.route('/articles/<string:article_slug>/comment', methods=['POST'])
@login_required
@permission_required(UserPermission.COMMENT)
def publish_comment(article_slug):
    """发表评论"""
    article = Article.get_by_slug(article_slug, deleted=False)
    if not article:
        return gen_error_json(errors.ARTICLE_NOT_EXISTS)
    form = CommentDetailForm(meta={'csrf': False})
    if not form.validate_on_submit():
        return gen_error_json(errors.ILLEGAL_FORM)
    Comment.create(
        body=form.body.data,
        author_id=current_user.id,
        article_id=article.id
    )
    return gen_success_json()


@blueprint.route('/comments/<int:comment_id>/modify', methods=['POST'])
@login_required
@permission_required(UserPermission.COMMENT)
def modify_comment(comment_id):
    """修改评论"""
    comment = Comment.get_by_id(comment_id, deleted=False)
    if not comment:
        return gen_error_json(errors.COMMENT_NOT_EXISTS)
    if comment.author_id != current_user.id:
        return gen_error_json(errors.USER_PERMISSION_DENIED)
    form = CommentDetailForm(meta={'csrf': False})
    if not form.validate_on_submit():
        return gen_error_json(errors.ILLEGAL_FORM)
    comment.update(body=form.body.data)
    return gen_success_json()


@blueprint.route('/send-message/<string:recipient_id>', methods=['POST'])
@login_required
@permission_required(UserPermission.MESSAGE)
def send_message(recipient_id):
    form = MessageForm(meta={'csrf': False})
    if not form.validate_on_submit():
        return gen_error_json(errors.ILLEGAL_FORM)
    if current_user.id == recipient_id:
        return gen_error_json(errors.INTERNAL_ERROR)
    user = User.get_by_id(recipient_id, deleted=False)
    if not user:
        return gen_error_json(errors.USER_NOT_EXISTS)
    Message.create(sender=current_user, recipient=user, body=form.body.data)
    return gen_success_json()


@blueprint.route('/messages/<string:filter_type>')
@login_required
def message_list(filter_type):
    page = request.args.get('page', 1, type=int)
    page_size = Constant.MESSAGE_PAGE_SIZE
    if filter_type == 'received':
        current_user.update(last_message_read_time=datetime.utcnow())
        pagination = current_user.message_received.order_by(Message.id.desc())\
            .paginate(page, page_size)
    elif filter_type == 'sent':
        pagination = current_user.message_sent.order_by(Message.id.desc())\
            .paginate(page, page_size)
    else:
        return gen_error_json(errors.FILTER_TYPE_ERROR)
    data = {
        'messages': [message.to_dict() for message in pagination.items]
    }
    data.update(page_meta_data(page, page_size, pagination.total))
    return gen_success_json(data)

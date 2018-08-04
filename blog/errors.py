class BaseError:
    __slots__ = ('code', 'message')

    def __init__(self, code, message):
        self.code = code
        self.message = message


BAD_REQUEST = BaseError('BAD_REQUEST', '无效的请求')
UNAUTHORIZED = BaseError('UNAUTHORIZED', '未登录')
PERMISSION_FORBIDDEN = BaseError('PERMISSION_FORBIDDEN', '没有权限')
QUERY_WORD_NOT_FOUND = BaseError('QUERY_WORD_NOT_FOUND', '找不到查找关键词')
CATEGORY_NOT_EXISTS = BaseError('CATEGORY_NOT_EXISTS', '目录不存在')
ARTICLE_NOT_EXISTS = BaseError('ARTICLE_NOT_EXISTS', '文章不存在')
COMMENT_NOT_EXISTS = BaseError('COMMENT_NOT_EXISTS', '评论不存在')
TAG_NOT_EXISTS = BaseError('TAG_NO_EXISTS', '标签不存在')
USER_NOT_EXISTS = BaseError('USER_NOT_EXISTS', '用户不存在')
ILLEGAL_FORM = BaseError('ILLEGAL_FORM', '无效的输入，请重试')
WRONG_EMAIL_OR_PASSWORD = BaseError('WRONG_EMAIL_OR_PASSWORD', '账号或密码错误')
NICKNAME_ALREADY_USED = BaseError('NICKNAME_ALREADY_USED', '该昵称已被使用')
EMAIL_ALREADY_REGISTERED = BaseError('EMAIL_ALREADY_REGISTERED', '该邮箱已被注册')
USER_PERMISSION_DENIED = BaseError('USER_PERMISSION_DENIED', '不允许的操作')
ALREADY_LOGIN = BaseError('ALREADY_LOGIN', '已经登录')
EMAIL_NOT_REGISTERED = BaseError('EMAIL_NOT_REGISTERED', '该邮箱未注册')
PASSWORD_RESET_TOKEN_INVALID = BaseError('PASSWORD_RESET_TOKEN_INVALID', '密码重置码无效')
INTERNAL_ERROR = BaseError('INTERNAL_ERROR', '服务器内部错误')
FILTER_TYPE_ERROR = BaseError('FILTER_TYPE_ERROR', '查询类型错误')

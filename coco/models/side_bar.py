import enum

from sqlalchemy_utils.types.choice import ChoiceType

from .mixin import db, Model


class SideBarStatus(enum.Enum):
    Shown = 1
    Hidden = 2


SideBarStatus.Shown.label = '展示'
SideBarStatus.Hidden.label = '隐藏'


class SideBarType(enum.Enum):
    HTML = 1
    LatestArticle = 2
    HottestArticle = 3
    LatestComment = 4


SideBarType.HTML.label = 'HTML'
SideBarType.LatestArticle.label = '最新文章'
SideBarType.HottestArticle.label = '最热文章'
SideBarType.LatestComment.label = '最新评论'


class SideBar(Model):
    """侧边栏表"""
    __tablename__ = 'side_bar'

    title = db.Column(db.String(60), nullable=False, comment='标题')
    content = db.Column(db.String(500), comment='内容')  # 如果不是 HTML 类型，可为空
    display_type = db.Column(
        db.SmallInteger(),
        ChoiceType(SideBarType, impl=db.SmallInteger),
        nullable=False,
        default=SideBarType.HTML,
        comment='展示类型'
    )
    status = db.Column(
        db.SmallInteger(),
        ChoiceType(SideBarStatus, impl=db.SmallInteger),
        nullable=False,
        default=SideBarStatus.Shown,
        comment='状态'
    )
    creator_id = db.Column(db.Integer(), nullable=False, index=True, comment='用户的ID')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __repr__(self):
        return f'<SideBar({self.title!r})>'

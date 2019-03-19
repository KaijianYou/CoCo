from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField
from wtforms.validators import InputRequired, Length, NumberRange


class ArticleDetailForm(FlaskForm):
    title = StringField(validators=[InputRequired(), Length(min=1, max=64)])
    content = StringField(validators=[InputRequired()])
    category_id = IntegerField(validators=[NumberRange(min=1)])
    tags = StringField(validators=[InputRequired(), Length(min=1, max=200)])


class CommentDetailForm(FlaskForm):
    content = StringField(validators=[InputRequired(), Length(min=1, max=200)])

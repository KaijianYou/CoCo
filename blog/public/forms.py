from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import InputRequired, Length


class CommentArticleForm(FlaskForm):
    body = StringField(validators=[InputRequired(), Length(min=1, max=200)])


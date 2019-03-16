from flask.helpers import get_env

from coco import create_app


ENV = get_env()
app = create_app(ENV)

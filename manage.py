from flask.helpers import get_env

from coco import create_app

CONFIG_ENV = get_env()
app = create_app(CONFIG_ENV)

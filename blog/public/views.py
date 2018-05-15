from flask import Blueprint

from blog.utils import generate_success_json


blueprint = Blueprint('public', __name__)


@blueprint.route('/', methods=['GET'])
def index():
    return generate_success_json()

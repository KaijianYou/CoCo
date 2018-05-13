from flask import Blueprint, jsonify


blueprint = Blueprint('public', __name__)


@blueprint.route('/', methods=['GET'])
def index():
    return jsonify('Hello World')
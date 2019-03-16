from flask import Flask
from elasticsearch import Elasticsearch

from coco.extensions import db, login_manager, migrate
from coco.settings import config
from coco.const import init_const


def create_app(config_env):
    app = Flask(__name__)
    app.config.from_object(config[config_env])
    config[config_env].init_app(app)
    try:
        init_app(app)
    except Exception as e:
        app.logger.error(e)
        raise e
    return app


def init_app(app):
    init_const(app.config['ENV'])

    register_extensions(app)
    register_blueprints(app)
    register_error_handler(app)
    register_shell_context(app)
    register_commands(app)


def register_extensions(app):
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    elasticsearch_url = app.config['ELASTICSEARCH_URL']
    setattr(app, 'elasticsearch', Elasticsearch([elasticsearch_url]) if elasticsearch_url else None)

    from .models.user import User, AnonymousUser
    login_manager.session_protection = 'basic'
    login_manager.anonymous_user = AnonymousUser

    @login_manager.user_loader
    def load_user(user_id):
        return User.get_by_id(int(user_id))


def register_blueprints(app):
    from coco import main, auth
    app.register_blueprint(auth.routes.blueprint, url_prefix='/api/auth')
    app.register_blueprint(main.routes.blueprint, url_prefix='/api')


def register_error_handler(app):
    from coco.utils.json_util import gen_error_json
    from coco.errors import BAD_REQUEST, PERMISSION_FORBIDDEN, UNAUTHORIZED, NOT_FOUND, METHOD_NOT_ALLOWED

    def bad_request(e):
        return gen_error_json(BAD_REQUEST)

    def unauthorized(e):
        return gen_error_json(UNAUTHORIZED)

    def permission_forbidden(e):
        return gen_error_json(PERMISSION_FORBIDDEN)

    def not_found(e):
        return gen_error_json(NOT_FOUND)

    def method_not_allowed(e):
        return gen_error_json(METHOD_NOT_ALLOWED)

    app.register_error_handler(400, bad_request)
    app.register_error_handler(401, unauthorized)
    app.register_error_handler(403, permission_forbidden)
    app.register_error_handler(404, not_found)
    app.register_error_handler(405, method_not_allowed)


def register_shell_context(app):
    def shell_context():
        return {
            'app': app,
            'db': db
        }
    app.shell_context_processor(shell_context)


def register_commands(app):
    from coco import commands
    app.cli.add_command(commands.test)

import sys
import traceback

from flask import Flask

from blog.extensions import db, login_manager, migrate
from blog.settings import config
from blog.const import init_const


def create_app(config_env):
    try:
        app = Flask(__name__)
        app.config.from_object(config[config_env])
        config[config_env].init_app(app)
        init_const(app.config['ENV'])
        register_extensions(app)
        register_blueprints(app)
        register_error_handler(app)
        register_shell_context(app)
        register_commands(app)
    except Exception:
        traceback.print_exc()
        sys.exit()
    else:
        return app


def register_extensions(app):
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    from .models.user import User, AnonymousUser
    login_manager.session_protection = 'basic'
    login_manager.anonymous_user = AnonymousUser

    @login_manager.user_loader
    def load_user(user_id):
        return User.get_by_id(int(user_id))


def register_blueprints(app):
    from blog import public, auth
    app.register_blueprint(auth.views.blueprint, url_prefix='/api/auth')
    app.register_blueprint(public.views.blueprint, url_prefix='/api')


def register_error_handler(app):
    from blog.utils.json_util import generate_error_json
    from blog.errors import BAD_REQUEST, PERMISSION_FORBIDDEN, UNAUTHORIZED

    def bad_request(e):
        return generate_error_json(BAD_REQUEST)

    def unauthorized(e):
        return generate_error_json(UNAUTHORIZED)

    def permission_forbidden(e):
        return generate_error_json(PERMISSION_FORBIDDEN)

    app.register_error_handler(400, bad_request)
    app.register_error_handler(401, unauthorized)
    app.register_error_handler(403, permission_forbidden)


def register_shell_context(app):
    def shell_context():
        return {
            'app': app,
            'db': db
        }
    app.shell_context_processor(shell_context)


def register_commands(app):
    from blog import commands
    app.cli.add_command(commands.test)
    app.cli.add_command(commands.urls)
    app.cli.add_command(commands.debug)
    app.cli.add_command(commands.shell)


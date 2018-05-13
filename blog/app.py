from flask import Flask

from . import commands, public
from .extensions import db, login_manager, migrate, mail
from .settings import config
from .const import init_const


def create_app(config_env):
    app = Flask(__name__)
    app.config.from_object(config[config_env])
    config[config_env].init_app(app)

    init_const(config_env)

    register_extensions(app)
    register_blueprints(app)
    register_shell_context(app)
    register_commands(app)
    return app


def register_extensions(app):
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)

    login_manager.session_protection = 'basic'

    from .models.user import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.get_by_id(int(user_id))


def register_blueprints(app):
    app.register_blueprint(public.views.blueprint)


def register_shell_context(app):
    def shell_context():
        return {
            'app': app,
            'db': db
        }
    app.shell_context_processor(shell_context)


def register_commands(app):
    app.cli.add_command(commands.test)

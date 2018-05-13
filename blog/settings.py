import os
import time

from flask import g
from flask_sqlalchemy import get_debug_queries


class Config:
    SECRET_KEY = os.environ['COCO_SECRET_KEY']

    # 启用数据库查询性能记录功能
    SQLALCHEMY_RECORD_QUERIES = True
    # 查询时间超过 0.1s 的语句将被记录
    SLOW_DB_QUERY_TIME = 0.1
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    # 分页设置
    ARTICLES_PER_PAGE = 10
    COMMENTS_PER_PAGE = 10

    def init_app(self, app):
        @app.before_request
        def before_request():
            g.name = app.config['ENV']
            g.request_start_time = time.time()
            request_time = (time.time() - g.request_start_time) * 1000
            g.request_time = lambda: f'{request_time:.0f}ms'

        @app.after_request
        def after_request(response):
            for func in getattr(g, 'call_after_request', ()):
                response = func(response)
            return response


class DevConfig(Config):
    ENV = 'development'

    DEBUG = True

    # 数据库配置
    SQLALCHEMY_DATABASE_URI = os.environ['COCO_DEV_DATABASE_URI']

    # 在 stderr 输出生成的 SQL 语句
    SQLALCHEMY_ECHO = True

    # 数据备份路径
    DB_BACKUP_PATH = 'var/www/db_backup'

    def init__app(self, app):
        super().__init__(app)

        @app.after_request
        def after_request(response):
            all_query_duration = 0
            all_query_count = 0
            for query in get_debug_queries():
                all_query_count += 1
                all_query_duration += query.duration
            plural = "query" if all_query_count == 1 else "queries"
            print(f'\033[92m[QUERY] {all_query_count} {plural} in {all_query_duration * 1000} ms\033[0m')
            for func in getattr(g, 'call_after_request', ()):
                response = func(response)
            return response


class TestConfig(Config):
    ENV = 'test'

    DEBUG = True
    TESTING = True

    # 禁用表单 CSRF 保护
    WTF_CSRF_ENABLED = False

    # 数据库配置
    SQLALCHEMY_DATABASE_URI = os.environ['COCO_TEST_DATABASE_URI']


class ProdConfig(Config):
    ENV = 'production'

    DEBUG = False

    # 数据库配置
    SQLALCHEMY_DATABASE_URI = os.environ['COCO_DATABASE_URI']

    # 数据备份路径
    DB_BACKUP_PATH = '/var/www/db_backup/'

    def init_app(self, app):
        super().init_app(app)

        import logging
        from logging.handlers import TimedRotatingFileHandler
        from logging import Formatter

        file_handler = TimedRotatingFileHandler(filename='/var/www/log/coco/',
                                                when='midnight',
                                                interval=1,
                                                backupCount=30)
        file_handler.setLevel(logging.WARNING)
        file_handler.suffix = '%Y-%m-%d.log'
        formatter = Formatter('%(levelname)s %(asctime)s %(pathname)s %(filenames)s %(module)s %(funcName)s %(lineno)d: %(message)s')
        file_handler.setFormatter(formatter)
        app.logger.addHandler(file_handler)

        # 日志记录执行缓慢的 SQL 语句
        @app.after_request
        def after_request(response):
            for query in get_debug_queries():
                if query.duration >= app.config['SLOW_DB_QUERY_TIME']:
                    app.logger.warning(query)
            for func in getattr(g, 'call_after_request', ()):
                response = func(response)
            return response


config = {
    DevConfig.ENV: DevConfig(),
    ProdConfig.ENV: ProdConfig(),
    TestConfig.ENV: TestConfig()
}

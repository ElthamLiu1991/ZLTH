import os

from flask import Blueprint


class Config(object):
    DEBUG = False
    base_dir = os.path.abspath('./')
    print("base_dir:", base_dir)
    SQLALCHEMY_DATABASE_URI = 'sqlite:///'+os.path.join(base_dir, 'database/database.sqlite3')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = "random string"


class ProductionConfig(Config):
    pass


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    DEBUG = True
    TESTING = True


class NestableBlueprint(Blueprint):
    def register_blueprint(self, blueprint, **options):
        def deferred(state):
            url_prefix = (state.url_prefix or u"") + (options.get('url_prefix', blueprint.url_prefix) or u"")
            if 'url_prefix' in options:
                del options['url_prefix']
            state.app.register_blueprint(blueprint, url_prefix=url_prefix, **options)
        self.record(deferred)

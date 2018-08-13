import logging
import os

from flask import Flask
from flask_assets import Bundle, Environment
from flask_login import LoginManager
from flask_session import Session
import redis

from response_operations_ui.cloud.cloudfoundry import ONSCloudFoundry
from response_operations_ui.logger_config import logger_initial_config
from response_operations_ui.user import User
from response_operations_ui.views import setup_blueprints


def create_app(config_name=None):
    app = Flask(__name__)

    # Load css and js assets
    assets = Environment(app)
    assets.url = app.static_url_path
    scss_min = Bundle('css/*', 'css/fonts/*', 'css/components/*',
                      filters=['cssmin'], output='minimised/all.min.css')
    assets.register('scss_all', scss_min)
    js_min = Bundle('js/*', filters='jsmin', output='minimised/all.min.js')
    assets.register('js_all', js_min)

    config_name = config_name or os.environ.get("APP_SETTINGS", "Config")
    app_config = f'config.{config_name}'
    app.config.from_object(app_config)

    app.url_map.strict_slashes = False
    app.secret_key = app.config['RESPONSE_OPERATIONS_UI_SECRET']

    logger_initial_config(service_name='response-operations-ui', log_level=app.config['LOGGING_LEVEL'])
    logger = logging.getLogger(__name__)
    logger.info('Logger created', level=app.config['LOGGING_LEVEL'])

    login_manager = LoginManager(app)
    login_manager.init_app(app)
    login_manager.login_view = "sign_in_bp.sign_in"

    @login_manager.user_loader
    def user_loader(user_id):
        return User(user_id)

    if app.config['SESSION_TYPE'] == 'redis':
        cf = ONSCloudFoundry()
        # If deploying in cloudfoundry set config to use cf redis instance
        if cf:
            redis_service_name = app.config['REDIS_SERVICE']
            logger.info('Cloudfoundry detected, setting service configurations')
            redis_service = cf.redis(redis_service_name)
            app.config['REDIS_HOST'] = redis_service.credentials['host']
            app.config['REDIS_PORT'] = redis_service.credentials['port']

        # wrap in the flask server side session manager and back it by redis
        app.config['SESSION_REDIS'] = redis.StrictRedis(host=app.config['REDIS_HOST'],
                                                        port=app.config['REDIS_PORT'],
                                                        db=app.config['REDIS_DB'])

    if app.config['DEBUG']:
        app.jinja_env.auto_reload = True

    Session(app)

    setup_blueprints(app)

    logger.info("App setup complete", config=config_name)

    return app

import copy
import logging
import os
import requestsdefaulter

import redis
from flask import Flask
from flask_assets import Environment
from flask_login import LoginManager
from flask_talisman import Talisman
from flask_wtf.csrf import CSRFProtect
from flask_zipkin import Zipkin
from structlog import wrap_logger
from flask_session import Session

from response_operations_ui.cloud.cloudfoundry import ONSCloudFoundry
from response_operations_ui.logger_config import logger_initial_config
from response_operations_ui.user import User
from response_operations_ui.views import setup_blueprints, reporting_unit_bp, messages_bp
from response_operations_ui.common.jinja_filters import filter_blueprint

cf = ONSCloudFoundry()

CSP_POLICY = {
    'default-src': ["'self'", 'https://cdn.ons.gov.uk'],
    'font-src': ["'self'", 'data:', 'https://fonts.gstatic.com', 'https://cdn.ons.gov.uk'],
    'script-src': ["'self'", 'https://www.googletagmanager.com', 'https://cdn.ons.gov.uk'],
    'connect-src': ["'self'", 'https://www.googletagmanager.com', 'https://tagmanager.google.com',
                    'https://cdn.ons.gov.uk'],
    'img-src': ["'self'", 'data:', 'https://www.gstatic.com', 'https://www.google-analytics.com',
                'https://www.googletagmanager.com', 'https://ssl.gstatic.com', 'https://cdn.ons.gov.uk'],
    'style-src': ["'self'", 'https://cdn.ons.gov.uk', "'unsafe-inline'", 'https://tagmanager.google.com',
                  'https://fonts.googleapis.com'],
}


class GCPLoadBalancer:

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        scheme = environ.get("HTTP_X_FORWARDED_PROTO", "http")
        if scheme:
            environ["wsgi.url_scheme"] = scheme
        return self.app(environ, start_response)


def create_app(config_name=None):
    csp_policy = copy.deepcopy(CSP_POLICY)
    app = Flask(__name__)

    Talisman(
        app,
        content_security_policy=csp_policy,
        content_security_policy_nonce_in=['script-src'],
        force_https=False,  # this is handled at the load balancer
        strict_transport_security=True,
        strict_transport_security_max_age=31536000,
        frame_options='DENY')
    app.name = "response_operations_ui"

    CSRFProtect(app)

    app_config = f'config.{config_name or os.environ.get("APP_SETTINGS", "Config")}'
    app.config.from_object(app_config)

    # Load css and js assets
    assets = Environment(app)

    if app.config['DEBUG'] or app.config['TESTING']:
        assets.cache = False
        assets.manifest = None

    if not app.config['DEBUG'] and not cf.detected:
        app.wsgi_app = GCPLoadBalancer(app.wsgi_app)

    assets.url = app.static_url_path

    app.jinja_env.add_extension('jinja2.ext.do')

    app.register_blueprint(filter_blueprint)

    app.url_map.strict_slashes = False
    app.secret_key = app.config['RESPONSE_OPERATIONS_UI_SECRET']

    # Zipkin
    zipkin = Zipkin(app=app, sample_rate=app.config.get("ZIPKIN_SAMPLE_RATE"))
    requestsdefaulter.default_headers(zipkin.create_http_headers_for_new_span)

    logger_initial_config(service_name='response-operations-ui', log_level=app.config['LOGGING_LEVEL'])
    logger = wrap_logger(logging.getLogger(__name__))
    logger.info('Logger created', log_level=app.config['LOGGING_LEVEL'])

    login_manager = LoginManager(app)
    login_manager.init_app(app)
    login_manager.login_view = "sign_in_bp.sign_in"

    @app.context_processor
    def inject_availability_message():

        redis_avail_msg = app.config['SESSION_REDIS']

        if len(redis_avail_msg.keys('AVAILABILITY_MESSAGE_RES_OPS')) == 1:
            return {
                "availability_message": redis_avail_msg.get('AVAILABILITY_MESSAGE_RES_OPS').decode('utf-8')
            }
        return {}

    @login_manager.user_loader
    def user_loader(user_id):
        return User(user_id)

    if cf.detected:
        with app.app_context():
            # If deploying in cloudfoundry set config to use cf redis instance
            logger.info('Cloudfoundry detected, setting service configurations')
            service = cf.redis
            app.config['REDIS_HOST'] = service.credentials['host']
            app.config['REDIS_PORT'] = service.credentials['port']

    # wrap in the flask server side session manager and back it by redis
    app.config['SESSION_REDIS'] = redis.StrictRedis(host=app.config['REDIS_HOST'],
                                                    port=app.config['REDIS_PORT'],
                                                    db=app.config['REDIS_DB'])

    app.jinja_environment.lstrip_blocks = True

    if app.config['DEBUG'] or os.environ.get('JINJA_RELOAD'):
        app.jinja_env.auto_reload = True

    Session(app)

    setup_blueprints(app)

    return app

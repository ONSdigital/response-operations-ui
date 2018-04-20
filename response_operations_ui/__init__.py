import logging
import os

from flask import Flask
from flask_assets import Bundle, Environment
from flask_login import LoginManager
from flask_session import Session
import redis
from flask_talisman import Talisman

from response_operations_ui.cloud.cloudfoundry import ONSCloudFoundry
from response_operations_ui.logger_config import logger_initial_config
from response_operations_ui.user import User

CSP_POLICY = {
    'default-src': ["'self'", 'https://cdn.ons.gov.uk', ],
    'font-src': ["'self'", 'data:', 'https://cdn.ons.gov.uk', ],
    'script-src': ["'self'", 'https://www.google-analytics.com', 'https://cdn.ons.gov.uk', ],
    'connect-src': ["'self'", 'https://www.google-analytics.com', 'https://cdn.ons.gov.uk', ],
    'img-src': ["'self'", 'data:', 'https://www.google-analytics.com', 'https://cdn.ons.gov.uk', ]
}

app = Flask(__name__)

# Load css and js assets
assets = Environment(app)
assets.url = app.static_url_path
scss_min = Bundle('css/*', 'css/fonts/*', 'css/components/*',
                  filters=['cssmin'], output='minimised/all.min.css')
assets.register('scss_all', scss_min)
js_min = Bundle('js/*', filters='jsmin', output='minimised/all.min.js')
assets.register('js_all', js_min)

app_config = 'config.{}'.format(os.environ.get('APP_SETTINGS', 'Config'))
app.config.from_object(app_config)

app.url_map.strict_slashes = False
app.secret_key = app.config['RESPONSE_OPERATIONS_UI_SECRET']

logger_initial_config(service_name='response-operations-ui', log_level=app.config['LOGGING_LEVEL'])
logger = logging.getLogger(__name__)

login_manager = LoginManager(app)
login_manager.init_app(app)
login_manager.login_view = "sign_in_bp.sign_in"

if app.config['SESSION_TYPE'] == 'redis':
    cf = ONSCloudFoundry()
    # If deploying in cloudfoundry set config to use cf redis instance
    if cf:
        redis_service_name = app.config['REDIS_SERVICE']
        logger.info('Cloudfoundry detected, setting service configurations')
        redis_service = cf.redis(redis_service_name)
        app.config['REDIS_HOST'] = redis_service.credentials['host']
        app.config['REDIS_PORT'] = redis_service.credentials['port']

    redis = redis.StrictRedis(host=app.config['REDIS_HOST'],
                              port=app.config['REDIS_PORT'],
                              db=app.config['REDIS_DB'])

    # wrap in the flask server side session manager and back it by redis
    app.config['SESSION_REDIS'] = redis

Talisman(app,
         content_security_policy=CSP_POLICY,
         content_security_policy_nonce_in=['script-src'],
         session_cookie_secure=True,  # Will setting True this cause issues when https is terminated?
         force_https=False,  # this is handled at the firewall
         strict_transport_security=True,
         strict_transport_security_max_age=31536000,
         strict_transport_security_include_subdomains=True,
         referrer_policy='same-origin',
         frame_options='DENY')

Session(app)


@login_manager.user_loader
def user_loader(user_id):
    return User(user_id)


import response_operations_ui.views  # NOQA # pylint: disable=wrong-import-position
import response_operations_ui.error_handlers  # NOQA # pylint: disable=wrong-import-position

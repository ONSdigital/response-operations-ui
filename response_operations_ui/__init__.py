import os
import redis

from flask import Flask
from flask_assets import Bundle, Environment
from flask_login import LoginManager
from flask_session import Session

from response_operations_ui.logger_config import logger_initial_config
from response_operations_ui.user import User


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

app.url_map.stricts_slashes = False
app.secret_key = app.config['RESPONSE_OPERATIONS_UI_SECRET']

logger_initial_config(service_name='response-operations-ui', log_level=app.config['LOGGING_LEVEL'])

login_manager = LoginManager(app)
login_manager.init_app(app)
login_manager.login_view = "sign_in_bp.sign_in"


redis = redis.StrictRedis(host=app.config['REDIS_HOST'],
                          port=app.config['REDIS_PORT'],
                          db=app.config['REDIS_DB'])

# wrap in the flask server side session manager and back it by redis
app.config['SESSION_REDIS'] = redis
Session(app)


@login_manager.user_loader
def user_loader(token):
    return User(token)


import response_operations_ui.views  # NOQA # pylint: disable=wrong-import-position
import response_operations_ui.error_handlers  # NOQA # pylint: disable=wrong-import-position

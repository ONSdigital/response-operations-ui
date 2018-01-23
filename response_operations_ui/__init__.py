import os

from flask import Flask
from flask_assets import Bundle, Environment
from flask_login import LoginManager

from response_operations_ui.logger_config import logger_initial_config
from response_operations_ui.user import User


app = Flask(__name__)
login_manager = LoginManager(app)
login_manager.init_app(app)
login_manager.login_view = "sign_in_bp.login"

# Load scss and js assets
assets = Environment(app)
assets.url = app.static_url_path
scss_min = Bundle('scss/*', 'scss/fonts/*', 'scss/components/*',
                  filters=['pyscss', 'cssmin'], output='minimised/all.min.css')
assets.register('scss_all', scss_min)
js_min = Bundle('js/*', filters='jsmin', output='minimised/all.min.js')
assets.register('js_all', js_min)

app_config = 'config.{}'.format(os.environ.get('APP_SETTINGS', 'Config'))
app.config.from_object(app_config)

app.url_map.strict_slashes = False
app.secret_key = app.config['RESPONSE_OPERATIONS_UI_SECRET']

logger_initial_config(service_name='response-operations-ui', log_level=app.config['LOGGING_LEVEL'])


@login_manager.user_loader
def user_loader(user_id):
    return User(user_id)

import response_operations_ui.views  # NOQA # pylint: disable=wrong-import-position

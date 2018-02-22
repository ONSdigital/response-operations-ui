import os

from flask import Flask
from flask_assets import Bundle, Environment
from flask_login import LoginManager

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

app.url_map.strict_slashes = False
app.secret_key = app.config['RESPONSE_OPERATIONS_UI_SECRET']

logger_initial_config(service_name='response-operations-ui', log_level=app.config['LOGGING_LEVEL'])

login_manager = LoginManager(app)
login_manager.init_app(app)
login_manager.login_view = "sign_in_bp.sign_in"


@login_manager.user_loader
def user_loader(token):
    # TODO This will need to be replaced with a call to reddis to get the token
    # as we can't leave that sort of information in the cookie.  Will be implemented
    # down the line once uaa is sorted out.
    return User(token)


import response_operations_ui.views  # NOQA # pylint: disable=wrong-import-position
import response_operations_ui.error_handlers  # NOQA # pylint: disable=wrong-import-position

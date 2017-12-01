import os

from flask import Flask
from flask_assets import Bundle, Environment

from response_operations_ui.logger_config import logger_initial_config


app = Flask(__name__)

# Load scss and js assets
assets = Environment(app)
assets.url = app.static_url_path
scss_min = Bundle('scss/test.scss', filters=['pyscss', 'cssmin'], output='minimised/all.css.min')
assets.register('scss_all', scss_min)
js_min = Bundle('js/test.js', filters='jsmin', output='minimised/all.js.min')
assets.register('js_all', js_min)

app_config = 'config.{}'.format(os.environ.get('APP_SETTINGS', 'Config'))
app.config.from_object(app_config)

app.url_map.strict_slashes = False

logger_initial_config(service_name='response-operations-ui', log_level=app.config['LOGGING_LEVEL'])


from response_operations_ui.views import hello  # NOQA # pylint: disable=wrong-import-position

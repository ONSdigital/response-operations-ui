import os

from flask import Flask

from response_operations_ui.logger_config import logger_initial_config


app = Flask(__name__)

app_config = 'config.{}'.format(os.environ.get('APP_SETTINGS', 'Config'))
app.config.from_object(app_config)

app.url_map.strict_slashes = False

logger_initial_config(service_name='response-operations-ui', log_level=app.config['LOGGING_LEVEL'])


from response_operations_ui.views import hello  # NOQA # pylint: disable=wrong-import-position

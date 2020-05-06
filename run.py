import logging
import os

from structlog import wrap_logger
from structlog.processors import JSONRenderer

from response_operations_ui import create_app


logger = wrap_logger(logging.getLogger(__name__),
                     processors=[JSONRenderer(indent=1, sort_keys=True)])


if __name__ == '__main__':
    if not os.getenv('APP_SETTINGS'):
        os.environ['APP_SETTINGS'] = 'DevelopmentConfig'
    app = create_app()
    logger.info("Starting listening on port {}".format(app.config['PORT']))
    app.run(debug=app.config['DEBUG'], host='0.0.0.0', port=int(app.config['PORT']))

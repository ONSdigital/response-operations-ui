import copy
import logging
import os

import redis
from flask import Flask, flash, redirect, session, url_for
from flask_assets import Environment
from flask_login import LoginManager
from flask_talisman import Talisman
from flask_wtf.csrf import CSRFError, CSRFProtect
from jinja2 import ChainableUndefined
from structlog import wrap_logger

from config import Config
from flask_session import Session
from response_operations_ui.common.jinja_filters import filter_blueprint
from response_operations_ui.controllers.uaa_controller import user_has_permission
from response_operations_ui.logger_config import logger_initial_config
from response_operations_ui.user import User
from response_operations_ui.views import setup_blueprints

CSP_POLICY = {
    "default-src": ["'self'", "https://cdn.ons.gov.uk"],
    "font-src": ["'self'", "data:", "https://fonts.gstatic.com", "https://cdn.ons.gov.uk"],
    "script-src": ["'self'", "https://www.googletagmanager.com", "https://cdn.ons.gov.uk", "https://code.jquery.com"],
    "connect-src": [
        "'self'",
        "https://www.googletagmanager.com",
        "https://tagmanager.google.com",
        "https://cdn.ons.gov.uk",
    ],
    "img-src": [
        "'self'",
        "data:",
        "https://www.gstatic.com",
        "https://www.google-analytics.com",
        "https://www.googletagmanager.com",
        "https://ssl.gstatic.com",
        "https://cdn.ons.gov.uk",
    ],
    "style-src": [
        "'self'",
        "https://cdn.ons.gov.uk",
        "'unsafe-inline'",
        "https://tagmanager.google.com",
        "https://fonts.googleapis.com",
    ],
}

ONE_YEAR_IN_SECONDS = 31536000
DEFAULT_REFERRER_POLICY = "strict-origin-when-cross-origin"


class GCPLoadBalancer:
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        scheme = environ.get("SCHEME", "http")
        if scheme:
            environ["wsgi.url_scheme"] = scheme
        return self.app(environ, start_response)


def create_app(config_name=None):
    csp_policy = copy.deepcopy(CSP_POLICY)
    app = Flask(__name__)

    app_config = f'config.{config_name or os.environ.get("APP_SETTINGS", "Config")}'
    app.config.from_object(app_config)

    if Config.WTF_CSRF_ENABLED:
        Talisman(
            app,
            content_security_policy=csp_policy,
            content_security_policy_nonce_in=["script-src"],
            force_https=False,  # this is handled at the load balancer
            strict_transport_security=True,
            strict_transport_security_max_age=ONE_YEAR_IN_SECONDS,
            referrer_policy=DEFAULT_REFERRER_POLICY,
            frame_options="SAMEORIGIN",
            frame_options_allow_from=None,
            session_cookie_secure=True,
            session_cookie_http_only=True,
        )
    app.name = "response_operations_ui"

    csrf = CSRFProtect(app)

    # Load css and js assets
    assets = Environment(app)

    if app.config["DEBUG"] or app.config["TESTING"]:
        assets.cache = False
        assets.manifest = None

    if not app.config["DEBUG"]:
        app.wsgi_app = GCPLoadBalancer(app.wsgi_app)

    assets.url = app.static_url_path

    app.jinja_env.undefined = ChainableUndefined
    app.jinja_env.add_extension("jinja2.ext.do")
    app.jinja_env.globals["hasPermission"] = user_has_permission

    app.register_blueprint(filter_blueprint)

    app.url_map.strict_slashes = False
    app.secret_key = app.config["RESPONSE_OPERATIONS_UI_SECRET"]

    logger_initial_config(service_name="response-operations-ui", log_level=app.config["LOGGING_LEVEL"])
    logger = wrap_logger(logging.getLogger(__name__))
    logger.info("Logger created", log_level=app.config["LOGGING_LEVEL"])

    login_manager = LoginManager(app)
    login_manager.init_app(app)
    login_manager.login_view = "sign_in_bp.sign_in"

    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        flash("Your session timed out", category="info")
        return redirect(url_for("logout_bp.logout"))

    @app.before_request
    def before_request():

        session.permanent = True  # set session to use PERMANENT_SESSION_LIFETIME
        session.modified = True  # reset the session timer on every request
        try:
            csrf.protect()

        except Exception as e:
            if e.code == 400:
                logger.warning(e.description)
            logger.warning(e)

    @app.context_processor
    def inject_availability_message():

        redis_avail_msg = app.config["SESSION_REDIS"]

        if len(redis_avail_msg.keys("AVAILABILITY_MESSAGE_RES_OPS")) == 1:
            return {"availability_message": redis_avail_msg.get("AVAILABILITY_MESSAGE_RES_OPS").decode("utf-8")}
        return {}

    @login_manager.user_loader
    def user_loader(user_id):
        username = session.get("username")
        return User(user_id, username)

    # wrap in the flask server side session manager and back it by redis
    app.config["SESSION_REDIS"] = redis.StrictRedis(
        host=app.config["REDIS_HOST"], port=app.config["REDIS_PORT"], db=app.config["REDIS_DB"]
    )

    app.jinja_environment.lstrip_blocks = True

    if app.config["DEBUG"] or os.environ.get("JINJA_RELOAD"):
        app.jinja_env.auto_reload = True

    Session(app)

    setup_blueprints(app)

    return app

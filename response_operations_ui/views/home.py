import logging

from flask import Blueprint, render_template
from flask_login import login_required
from structlog import wrap_logger
from structlog.processors import JSONRenderer


logger = wrap_logger(logging.getLogger(__name__),
                     processors=[JSONRenderer(indent=1, sort_keys=True)])

home_bp = Blueprint('home_bp', __name__, static_folder='static', template_folder='templates')


@home_bp.route('/', methods=['GET'])
@login_required
def home():
    return render_template('home.html')

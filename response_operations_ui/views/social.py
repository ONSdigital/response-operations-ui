import logging

from flask import Blueprint, render_template
from flask_login import login_required
from structlog import wrap_logger

logger = wrap_logger(logging.getLogger(__name__))
social_bp = Blueprint('social_bp', __name__,
                      static_folder='static', template_folder='templates')


@social_bp.route('/', methods=['GET', 'POST'])
@login_required
def social_case_search():
    return render_template('social.html')

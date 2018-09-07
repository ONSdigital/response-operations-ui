from flask import Blueprint

from response_operations_ui.views.social.social_case_search import social_case_search
from response_operations_ui.views.social.social_view_case_details import view_social_case_details
from response_operations_ui.views.social.generate_iac import generate_iac

social_bp = Blueprint('social_bp', __name__,
                      static_folder='static', template_folder='templates')

social_bp.add_url_rule('/', view_func=social_case_search, methods=['GET'])
social_bp.add_url_rule('/case/<case_id>', view_func=view_social_case_details, methods=['GET'])
social_bp.add_url_rule('/iac', view_func=generate_iac, methods=['POST'])

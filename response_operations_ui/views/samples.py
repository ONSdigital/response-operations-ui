from flask import Blueprint, render_template, make_response
from flask_login import login_required
from response_operations_ui.controllers import sample_controllers

sample_bp = Blueprint('sample_bp', __name__,
                      static_folder='static', template_folder='templates')


@sample_bp.route('/<sample_uuid>/notes', methods=['GET'])
@login_required
def view_collection_exercise(sample_uuid):
    sample_summary = sample_controllers.get_sample_summary(sample_uuid)

    body = render_template('sample_summary_notes.txt',
                           summary=sample_summary)
    headers = {'Content-Type': 'text/plain'}
    return make_response(body, 200, headers)

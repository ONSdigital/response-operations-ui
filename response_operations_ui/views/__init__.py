from response_operations_ui import app
from response_operations_ui.views.collection_exercise import collection_exercise_bp
from response_operations_ui.views.errors import error_bp
from response_operations_ui.views.home import home_bp
from response_operations_ui.views.info import info_bp
from response_operations_ui.views.logout import logout_bp
from response_operations_ui.views.messages import messages_bp
from response_operations_ui.views.reporting_units import reporting_unit_bp
from response_operations_ui.views.sign_in import sign_in_bp
from response_operations_ui.views.surveys import surveys_bp
from response_operations_ui.views.reporting_units_mock import reporting_units_mock_bp
from response_operations_ui.views.messages import messages_bp


app.register_blueprint(collection_exercise_bp, url_prefix='/surveys')
app.register_blueprint(error_bp, url_prefix='/errors')
app.register_blueprint(home_bp, url_prefix='/')
app.register_blueprint(info_bp, url_prefix='/info')
app.register_blueprint(logout_bp, url_prefix='/logout')
app.register_blueprint(messages_bp, url_prefix='/messages')
app.register_blueprint(reporting_unit_bp, url_prefix='/reporting-units')
app.register_blueprint(sign_in_bp, url_prefix='/sign-in')
app.register_blueprint(surveys_bp, url_prefix='/surveys')
app.register_blueprint(reporting_units_mock_bp, url_prefix='/reporting-units')

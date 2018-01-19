from response_operations_ui import app
from response_operations_ui.views.info import info_bp
from response_operations_ui.views.logout import logout_bp
from response_operations_ui.views.sign_in import sign_in_bp
from response_operations_ui.views.surveys import surveys_bp

app.register_blueprint(info_bp, url_prefix='/info')
app.register_blueprint(logout_bp, url_prefix='/logout')
app.register_blueprint(sign_in_bp, url_prefix='/')
app.register_blueprint(surveys_bp, url_prefix='/surveys')

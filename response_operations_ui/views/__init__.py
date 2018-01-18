from response_operations_ui import app
from response_operations_ui.views.home import home_bp
from response_operations_ui.views.surveys import surveys_bp
from response_operations_ui.views.info import info_bp


app.register_blueprint(home_bp, url_prefix='/')
app.register_blueprint(surveys_bp, url_prefix='/surveys')
app.register_blueprint(info_bp, url_prefix='/info')

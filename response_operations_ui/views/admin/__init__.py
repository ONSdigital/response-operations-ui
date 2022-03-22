from flask import Blueprint

admin_bp = Blueprint("admin_bp", __name__, static_folder="static", template_folder="templates")

from response_operations_ui.views.admin import banner, manage_user_accounts  # NOQA

from flask import Blueprint, redirect, request, make_response, url_for


logout_bp = Blueprint('logout_bp', __name__, static_folder='static', template_folder='templates')


@logout_bp.route('/')
def logout():
    # Delete user session in redis
    session_key = request.cookies.get('authorization')
    session = SessionHandler()
    session.delete_session(session_key)

    # Delete session cookie
    response = make_response(redirect(url_for('sign_in_bp.login')))
    response.set_cookie('authorization', value='', expires=0)
    return response

import logging

from flask import abort, redirect, render_template, request, url_for, Blueprint, current_app as app
from itsdangerous import URLSafeSerializer, BadSignature
from structlog import wrap_logger

from response_operations_ui.forms import ForgotPasswordForm
from response_operations_ui.controllers import party_controller, uaa_controller
from response_operations_ui.controllers.notify_controller import NotifyController
from response_operations_ui.exceptions.exceptions import UserDoesNotExist, NotifyError
from response_operations_ui.common import token_decoder

logger = wrap_logger(logging.getLogger(__name__))

BAD_AUTH_ERROR = 'Unauthorized user credentials'

passwords_bp = Blueprint('passwords_bp', __name__, static_folder='static', template_folder='templates')

@passwords_bp.route('/forgot-password', methods=['GET'])
def get_forgot_password():
    form = ForgotPasswordForm(request.form)
    return render_template('forgot-password.html', form=form)


@passwords_bp.route('/forgot-password', methods=['POST'])
def post_forgot_password():
    form = ForgotPasswordForm(request.form)
    form.email_address.data = form.email_address.data.strip()
    email = form.data.get('email_address')

    encoded_email = URLSafeSerializer(app.config['SECRET_KEY']).dumps(email)

    if form.validate():
        first_name = uaa_controller.get_first_name_by_email(email)
        if (first_name != ""):
            internal_url = app.config['RAS_INTERNAL_WEBSITE_URL']
            verification_url = f'{internal_url}/passwords/reset-password/{token_decoder.generate_email_token(email)}'

            personalisation = {
                'RESET_PASSWORD_URL': verification_url,
                'FIRST_NAME': first_name
            }

            try:
                NotifyController(app.config).request_to_notify(email=email,
                                                               template_name='confirm_password_change',
                                                               personalisation=personalisation)
            except NotifyError:
                logger.error('Error sending password change request email to Notify Gateway')
                return render_template('forgot-password-error.html')

            logger.info('Successfully sent password change request email')
        else:
            # We stil want to render the template for an email without an account to avoid 
            # people fishing for valid emails
            logger.info('Requested password reset for email not in UAA', email=encoded_email)

        return redirect(url_for('passwords_bp.forgot_password_check_email', email=encoded_email))

    return render_template('forgot-password.html', form=form, email=email)


@passwords_bp.route('/forgot-password/check-email', methods=['GET'])
def forgot_password_check_email():
    encoded_email = request.args.get('email', None)

    if encoded_email is None:
        logger.error('No email parameter supplied')
        return redirect(url_for('passwords_bp.get_forgot_password'))

    try:
        email = URLSafeSerializer(app.config['SECRET_KEY']).loads(encoded_email)
    except BadSignature:
        logger.error('Unable to decode email from URL', encoded_email=encoded_email)
        abort(404)
    
    return render_template('forgot-password-check-email.html', email=email)

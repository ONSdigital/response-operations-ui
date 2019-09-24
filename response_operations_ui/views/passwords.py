import logging

from flask import abort, redirect, render_template, request, url_for, Blueprint, current_app as app
from itsdangerous import URLSafeSerializer, BadSignature, SignatureExpired, BadData
from structlog import wrap_logger

from response_operations_ui.forms import ForgotPasswordForm, ResetPasswordForm
from response_operations_ui.controllers import uaa_controller
from response_operations_ui.controllers.notify_controller import NotifyController
from response_operations_ui.exceptions.exceptions import NotifyError
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

    if form.validate():
        return send_password_change_email(email)

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


@passwords_bp.route('/reset-password/<token>', methods=['GET'])
def get_reset_password(token, form_errors=None):
    form = ResetPasswordForm(request.form)

    try:
        duration = app.config['EMAIL_TOKEN_EXPIRY']
        token_decoder.decode_email_token(token, duration)
    except SignatureExpired:
        logger.warning('Token expired for Response Operations password reset', token=token)
        return render_template('reset-password-expired.html', token=token)
    except (BadSignature, BadData):
        logger.warning('Invalid token sent to Response Operations password reset', token=token)
        return render_template('reset-password-expired.html', token=token)

    template_data = {
        "error": {
            "type": form_errors
        },
        'token': token
    }
    return render_template('reset-password.html', form=form, data=template_data)


@passwords_bp.route('/reset-password/<token>', methods=['POST'])
def post_reset_password(token):
    form = ResetPasswordForm(request.form)

    if not form.validate():
        return get_reset_password(token, form_errors=form.errors)

    password = request.form.get('password')

    try:
        duration = app.config['EMAIL_TOKEN_EXPIRY']
        email = token_decoder.decode_email_token(token, duration)
    except SignatureExpired:
        logger.warning('Token expired for Response Operations password reset', token=token)
        return render_template('reset-password-expired.html', token=token)
    except (BadSignature, BadData):
        logger.warning('Invalid token sent to Response Operations password reset', token=token)
        return render_template('reset-password-expired.html', token=token)

    if (uaa_controller.change_user_password(email, password)):
        logger.info('Successfully changed user password', token=token)
        return redirect(url_for('passwords_bp.reset_password_confirmation'))

    logger.warning('Error changing password in UAA', token=token)
    return render_template('reset-password-error.html')


@passwords_bp.route('/reset-password/confirmation', methods=['GET'])
def reset_password_confirmation():
    return render_template('passwords/reset-password-confirmation.html')


@passwords_bp.route('/resend-password-email-expired-token/<token>', methods=['GET'])
def resend_password_email_expired_token(token):
    email = token_decoder.decode_email_token(token)
    return send_password_change_email(email)


def send_password_change_email(email):
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
        logger.info('Requested password reset for email not in UAA')

    return redirect(url_for('passwords_bp.forgot_password_check_email'))

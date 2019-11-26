import logging
from structlog import wrap_logger
from flask import Blueprint, request, render_template, redirect, url_for, abort, flash, current_app as app
from itsdangerous import URLSafeSerializer, BadSignature, BadData, SignatureExpired

from response_operations_ui.forms import RequestAccountForm, CreateAccountForm
from response_operations_ui.controllers import uaa_controller
from response_operations_ui.controllers.notify_controller import NotifyController
from response_operations_ui.common import token_decoder
from response_operations_ui.exceptions.exceptions import NotifyError

logger = wrap_logger(logging.getLogger(__name__))

account_bp = Blueprint('account_bp', __name__, static_folder='static', template_folder='templates')


@account_bp.route('/request-new-account', methods=['GET'])
def get_request_new_account(form_errors=None, email=None):
    form = RequestAccountForm(request.form)
    template_data = {
        "error": {
            "type": form_errors
        }
    }
    return render_template('request-new-account.html', form=form, data=template_data, email=email)


@account_bp.route('/request-new-account', methods=['POST'])
def post_request_new_account():
    form = RequestAccountForm(request.form)
    form.email_address.data = form.email_address.data.strip()
    email = form.data.get('email_address')

    if form.validate():
        local_part, domain_part = email.rsplit('@', 1)
        logger.info('This is the domain part', domain_part=domain_part)
        if domain_part != 'ons.gov.uk' and domain_part != 'ext.ons.gov.uk' and domain_part != 'ons.fake':
            logger.info('Account requested for non-ONS email address')
            errors = {'email_address': ['Not a valid ONS email address']}
            return get_request_new_account(form_errors=errors, email=email)

        password = form.data.get('password')
        admin_password = app.config['CREATE_ACCOUNT_ADMIN_PASSWORD']
        if password != admin_password:
            logger.info('Invalid password provided for create account')
            errors = {'password': ['Incorrect admin secret']}
            return get_request_new_account(form_errors=errors, email=email)

        return send_create_account_email(email)

    errors = {'email_address': ['Not a valid ONS email address']}
    return get_request_new_account(form_errors=errors, email=email)


@account_bp.route('/account-exists', methods=['GET'])
def request_new_account_account_exists():
    encoded_email = request.args.get('email')

    if encoded_email is None:
        logger.error('No email parameter supplied')
        return redirect(url_for('account_bp.get_request_new_account'))

    try:
        email = URLSafeSerializer(app.config['SECRET_KEY']).loads(encoded_email)
    except BadSignature:
        logger.error('Unable to decode email from URL', encoded_email=encoded_email)
        abort(404)

    return render_template('request-new-account-exists.html', email=email)


@account_bp.route('/request-new-account-check-email', methods=['GET'])
def request_new_account_check_email():
    encoded_email = request.args.get('email')

    if encoded_email is None:
        logger.error('No email parameter supplied')
        return redirect(url_for('passwords_bp.get_request_new_account'))

    try:
        email = URLSafeSerializer(app.config['SECRET_KEY']).loads(encoded_email)
    except BadSignature:
        logger.error('Unable to decode email from URL', encoded_email=encoded_email)
        abort(404)

    return render_template('request-new-account-check-email.html', email=email)


def send_create_account_email(email):
    url_safe_serializer = URLSafeSerializer(app.config['SECRET_KEY'])

    response = uaa_controller.get_user_by_email(email)
    if response.status_code != 200:
        logger.error('Error retrieving user from UAA', status_code=response.status_code,
                     email=url_safe_serializer.dumps(email))
        return render_template('request-new-account-error.html')

    if response.json()['totalResults'] == 0:
        internal_url = app.config['INTERNAL_WEBSITE_URL']
        verification_url = f'{internal_url}/account/create-account/{token_decoder.generate_email_token(email)}'

        logger.info('Sending create account email', verification_url=verification_url)

        personalisation = {
            'CREATE_ACCOUNT_URL': verification_url,
            'EMAIL': email
        }

        try:
            NotifyController().request_to_notify(email=email,
                                                 template_name='request_create_account',
                                                 personalisation=personalisation)
        except NotifyError as e:
            logger.error('Error sending create account request email to Notify Gateway', msg=e.description)
            return render_template('request-new-account-error.html')

        logger.info('Successfully sent create account request email', email=url_safe_serializer.dumps(email))
    else:
        logger.info('Requested account creation for email already in UAA', email=url_safe_serializer.dumps(email))
        return redirect(url_for('account_bp.request_new_account_account_exists',
                                email=url_safe_serializer.dumps(email)))

    return redirect(url_for('account_bp.request_new_account_check_email', email=url_safe_serializer.dumps(email)))


@account_bp.route('/resend_account_email_expired_token/<token>', methods=['GET'])
def resend_account_email_expired_token(token):
    email = token_decoder.decode_email_token(token)
    return send_create_account_email(email)


@account_bp.route('/create-account/<token>', methods=['GET'])
def get_create_account(token, form_errors=None):
    form = CreateAccountForm(request.form)

    try:
        duration = app.config['EMAIL_TOKEN_EXPIRY']
        _ = token_decoder.decode_email_token(token, duration)
    except SignatureExpired:
        logger.warning('Token expired for Response Operations account creation', token=token)
        return render_template('request-new-account-expired.html', token=token)
    except (BadSignature, BadData):
        logger.warning('Invalid token sent to Response Operations account creation', token=token)
        return render_template('request-new-account-expired.html', token=token)

    template_data = {
        "error": {
            "type": form_errors
        },
        'token': token
    }
    return render_template('create-new-account.html', form=form, data=template_data)


@account_bp.route('/create-account/<token>', methods=['POST'])
def post_create_account(token):
    form = CreateAccountForm(request.form)

    if not form.validate():
        return get_create_account(token, form_errors=form.errors)

    try:
        duration = app.config['EMAIL_TOKEN_EXPIRY']
        email = token_decoder.decode_email_token(token, duration)
    except SignatureExpired:
        logger.warning('Token expired for Response Operations create account', token=token)
        return render_template('request-new-account-expired.html', token=token)
    except (BadSignature, BadData):
        logger.warning('Invalid token sent to Response Operations create account', token=token)
        return render_template('request-new-account-expired.html', token=token)

    password = request.form.get('password')
    user_name = request.form.get('user_name')
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')

    response = uaa_controller.create_user_account(email, password, user_name, first_name, last_name)

    if response is not None:
        if response.status_code == 201:
            logger.info('Successfully created user account', token=token)
            send_confirm_created_email(email, first_name)
            flash('Account successfully created', category='account_created')
            return redirect(url_for('sign_in_bp.sign_in'))
        if response.status_code == 409:
            # Username already exists
            form_errors = {'user_name': ["Username already in use; please choose another"]}
            return get_create_account(form_errors=form_errors, token=token)

    return render_template('create-new-account-error.html')


def send_confirm_created_email(email, first_name):
    personalisation = {
        'FIRST_NAME': first_name
    }

    try:
        NotifyController().request_to_notify(email=email,
                                             template_name='confirm_create_account',
                                             personalisation=personalisation)
    except NotifyError as e:
        # This shouldn't show the client an error - the account creation was still successful.
        # They just won't get a confirmation email
        logger.error('Error sending account creation confirmation email to Notify Gateway', msg=e.description)

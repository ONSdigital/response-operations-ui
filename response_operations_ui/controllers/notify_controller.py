import logging

import structlog
import requests

from response_operations_ui.exceptions.exceptions import NotifyError

logger = structlog.wrap_logger(logging.getLogger(__name__))


class NotifyController:
    def __init__(self, config):
        self.config = config
        self.notify_url = config['NOTIFY_SERVICE_URL']
        self.request_password_change_template = config['NOTIFY_REQUEST_PASSWORD_CHANGE_TEMPLATE']
        self.confirm_password_change_template = config['NOTIFY_CONFIRM_PASSWORD_CHANGE_TEMPLATE']

    def _send_message(self, email, template_id, personalisation=None, reference=None):
        """
        Send message to gov.uk notify wrapper
        :param email: email address of recipient
        :param template_id: the template id on gov.uk notify to use
        :param personalisation: placeholder values in the template
        :param reference: reference to be generated if not using Notify's id
        :rtype: 201 if success
        """

        if not self.config['SEND_EMAIL_TO_GOV_NOTIFY']:
            logger.info("Notification not sent. Notify is disabled.")
            return

        notification = {
            "emailAddress": email,
        }
        if personalisation:
            notification.update({"personalisation": personalisation})
        if reference:
            notification.update({"reference": reference})

        url = f'{self.notify_url}{str(template_id)}'

        response = requests.post(url, json=notification)
        if response.status_code == 201:
            logger.info('Notification id sent via Notify-Gateway to GOV.UK Notify.', id=response.json()["id"])
        else:
            ref = reference if reference else 'reference_unknown'
            raise NotifyError("There was a problem sending a notification to Notify-Gateway to GOV.UK Notify",
                              reference=ref)

    def request_to_notify(self, email, template_name, personalisation=None, reference=None):
        template_id = self._get_template_id(template_name)
        self._send_message(email, template_id, personalisation, reference)

    def _get_template_id(self, template_name):
        templates = {'confirm_password_change': self.confirm_password_change_template,
                     'request_password_change': self.request_password_change_template}
        if template_name in templates:
            return templates[template_name]
        else:
            raise KeyError('Template does not exist')

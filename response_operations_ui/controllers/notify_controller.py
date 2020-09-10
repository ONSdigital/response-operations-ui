import json
import logging
import structlog
from response_operations_ui.exceptions.exceptions import NotifyError
from flask import current_app as app
from google.cloud import pubsub_v1

logger = structlog.wrap_logger(logging.getLogger(__name__))


class NotifyController:
    def __init__(self):
        self.request_password_change_template = app.config['NOTIFY_REQUEST_PASSWORD_CHANGE_TEMPLATE']
        self.confirm_password_change_template = app.config['NOTIFY_CONFIRM_PASSWORD_CHANGE_TEMPLATE']
        self.request_create_account_template = app.config['NOTIFY_REQUEST_CREATE_ACCOUNT_TEMPLATE']
        self.confirm_create_account_template = app.config['NOTIFY_CONFIRM_CREATE_ACCOUNT_TEMPLATE']
        self.topic_id = app.config['PUBSUB_TOPIC']
        self.project_id = app.config['GOOGLE_CLOUD_PROJECT']
        self.publisher = None

    def _send_message(self, email, template_id, personalisation):
        """
        Send message to gov.uk notify via pubsub topic
        :param email: str email address of recipient
        :param template_id: the template id on gov.uk notify to be used
        :param personalisation: personalisation if required
        """
        if not app.config['SEND_EMAIL_TO_GOV_NOTIFY']:
            logger.info("Notification not sent. Notify is disabled.")
            return

        notification = {
            'notify': {
                'email_address': email,
                'template_id': template_id,
                'personalisation': {}
            }
        }
        if personalisation:
            notification['notify']['personalisation'] = personalisation

        notification_str = json.dumps(notification)
        if self.publisher is None:
            self.publisher = pubsub_v1.PublisherClient()
        topic_path = self.publisher.topic_path(self.project_id, self.topic_id)
        logger.info('Publishing notification message to pub-sub topic', pubsub_topic=self.topic_id)
        future = self.publisher.publish(topic_path, data=notification_str.encode())
        # It's okay for us to catch a broad Exception here because the documentation for future.result() says it
        # throws either a TimeoutError or an Exception.
        try:
            msg_id = future.result()
            logger.info('Notification message published to pub-sub.', msg_id=msg_id, pubsub_topic=self.topic_id)
        except TimeoutError as e:
            raise NotifyError('There was a problem sending a notification via pub-sub topic to GOV.UK Notify.'
                              'Communication to pub-sub topic timed-out',
                              pubsub_topic=self.topic_id, error=e)
        except Exception as e:
            raise NotifyError('There was a problem sending a notification via pub-sub topic to GOV.UK Notify. '
                              'Communication to pub-sub topic raised an exception.', pubsub_topic=self.topic_id,
                              error=e)

    def request_to_notify(self, email, template_name, personalisation):
        template_id = self._get_template_id(template_name)
        self._send_message(email, template_id, personalisation)

    def _get_template_id(self, template_name):
        templates = {'confirm_password_change': self.confirm_password_change_template,
                     'request_password_change': self.request_password_change_template,
                     'confirm_create_account': self.confirm_create_account_template,
                     'request_create_account': self.request_create_account_template}
        if template_name in templates:
            return templates[template_name]
        else:
            raise KeyError('Template does not exist')

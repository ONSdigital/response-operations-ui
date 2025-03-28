import requests
from flask import current_app

from response_operations_ui.oidc.oidc import OIDCCredentialsService


def fetch_and_apply_oidc_credentials(session: requests.Session, client_id: str) -> None:
    # Type ignore: oidc_credentials_service is a singleton of this application
    oidc_credentials_service: OIDCCredentialsService = current_app["oidc_credentials_service"]  # type: ignore

    credentials = oidc_credentials_service.get_credentials(iap_client_id=client_id)
    credentials.apply(headers=session.headers)

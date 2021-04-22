import json
from json import JSONDecodeError

from google.oauth2 import service_account
from google.auth import crypt


def get_google_credentials(credentials_json):
    try:
        info = json.loads(credentials_json or '')
    except (TypeError, JSONDecodeError) as e:
        raise ValueError('Service account info was not in the expected format, should be valid json')

    if 'token_uri' not in info and 'client_email' not in info:
        raise ValueError('Service account info not in the expected format, both token_uri and client_email required')

    signer = crypt.RSASigner.from_service_account_info(info)

    return service_account.Credentials(
        signer,
        service_account_email=info["client_email"],
        token_uri=info["token_uri"],
        project_id=info.get("project_id")
    )

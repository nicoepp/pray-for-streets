import json
import os
from django.utils.crypto import get_random_string
from sendgrid.helpers.mail import Mail, To
from sendgrid import SendGridAPIClient
import requests


def segments_to_geojson(segments, street_name=None):
    features = []
    for segment in segments:
        features.append({
            'id': segment['pk'],
            'type': "Feature",
            'properties': {
                'STREET_NAME': street_name if street_name else segment['street__name']
            },
            'geometry': {
                'type': 'LineString',
                'coordinates': segment['path'] if segment['path'] else []
            }
        })

    return {
        "type": "FeatureCollection",
        "features": features,
    }


def recaptcha_valid(token, remoteip=None):
    if 'RECAPTCHA_SECRET_KEY' in os.environ:
        secret = os.environ['RECAPTCHA_SECRET_KEY']
    else:
        secret = '6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe'
    try:
        content = requests.post(
            'https://www.google.com/recaptcha/api/siteverify',
            data={
                'secret': secret,
                'response': token,
            }   # add remoteip
        ).content
    except requests.RequestException as e:
        return False
    data = json.loads(content)
    if 'success' not in data:
        return False
    return data['success']


FROM_EMAIL = 'Abbotsford Neighbourhood Prayer Walk <info@prayforabbotsford.com>'
TEMPLATE_ID = 'd-5f4bb94f40e3414a9784f9699b31e429'


def send_confirmation_mail(name, email, token, street_name=''):
    message = Mail(from_email=FROM_EMAIL, to_emails=[(email, name)])
    # pass custom values for our HTML placeholders
    message.dynamic_template_data = {
        'person_name': name,
        'street_name': street_name,
        'email_token': token,
    }
    message.template_id = TEMPLATE_ID

    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sg.send(message)
        code, body, headers = response.status_code, response.body, response.headers
        print(f"Confirmation email sent to: {name} <{email}>")
        print(f"Response code: {code}, body: {body}")
        return True
    except Exception as e:
        print("Confirmation email sending error: {0}".format(e))
        print(f'Tried sending to: {name} <{email}>')
        return False


def get_email_token():
    return get_random_string(20)

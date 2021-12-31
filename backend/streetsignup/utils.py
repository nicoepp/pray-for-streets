import json
import os
import sys

from django.utils.crypto import get_random_string
from mailjet_rest.client import ApiError

from mailjet_rest import Client
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


MJ_APIKEY_PUBLIC = os.environ.setdefault('MJ_APIKEY_PUBLIC', '')
MJ_APIKEY_PRIVATE = os.environ.setdefault('MJ_APIKEY_PRIVATE', '')


def send_confirmation_mail(name, email, token, street_name, city):
    """
    This call sends a message to the given recipient with vars and custom vars.
    """
    homepage = city.homepage.get()
    site = homepage.get_site()

    template_id = 3131695

    if 'abbotsford' in site.hostname:
        template_id = 3131695
    elif 'burnaby' in site.hostname:
        template_id = 3135239
    elif 'surrey' in site.hostname:
        template_id = 3135245
    elif 'vancouver' in site.hostname:
        template_id = 3135247

    if not MJ_APIKEY_PUBLIC or not MJ_APIKEY_PRIVATE:
        print('Confirmation email sending error: MailJet Env vars should be set!')
        return False

    mailjet = Client(auth=(MJ_APIKEY_PUBLIC, MJ_APIKEY_PRIVATE), version='v3.1')
    data = {
        'Messages': [
            {
                "From": {
                    "Email": f"info@{site.hostname}",
                    "Name": f"thePRAYERWALK | {city.name}"
                },
                "To": [{"Email": email, "Name": name}],
                "TemplateID": template_id,
                "TemplateLanguage": True,
                "Subject": "Thank you for praying with us! Confirm your Email",
                "Variables": {
                    "person_name": name,
                    "street_name": street_name,
                    "confirm_link": f"{site.root_url}/email/confirm/{token}"
                }
            }
        ]
    }
    try:
        resp = mailjet.send.create(data=data)

        if not resp.status_code // 100 == 2:  # not 2xx
            print("Confirmation email sending error: {0}".format(resp.reason))
            print(f'Tried sending to: {name} <{email}>')
            sys.stdout.flush()
            return False
        print(f"Confirmation email sent to: {name} <{email}> => ", resp.content)
        sys.stdout.flush()
        return True
    except ApiError as e:
        print("Confirmation email sending error: {0}".format(e))
        print(f'Tried sending to: {name} <{email}>')
        sys.stdout.flush()
        return False


def get_email_token():
    return get_random_string(25)


def ask_for_consent_email(name, email, token):
    pass


def send_street_co_subscriber_list(name, email, subscribers, street_name):
    pass


CONTACT_LIST_ID = {
    "Abbotsford": 48596,
    "Burnaby": 48040,
    "South Surrey": 48597,
    "Vancouver": 48598
}


def add_to_mailjet(contact, cities: []):
    results = set()
    if not MJ_APIKEY_PUBLIC or not MJ_APIKEY_PRIVATE:
        print('Confirmation email sending error: MailJet Env vars should be set!')
        return False

    mailjet = Client(auth=(MJ_APIKEY_PUBLIC, MJ_APIKEY_PRIVATE), version='v3')
    try:
        for city in cities:
            list_id = CONTACT_LIST_ID[city.name]
            data = {
                'Name': contact.name,
                'Properties': {},
                'Action': "addnoforce",
                'Email': contact.email
            }
            resp = mailjet.contactslist_managecontact.create(id=list_id, data=data)

            if not resp.status_code // 100 == 2:  # not 2xx
                print("Add contact error: {0}".format(resp.reason))
                print(f'Tried adding: {contact.name} <{contact.email}> to {city.name}')
                sys.stdout.flush()
                results.add(False)
                continue
            print(f"Add contact successful: {contact.name} <{contact.email}> to {city.name} => ", resp.content)
            sys.stdout.flush()
            results.add(True)
    except ApiError as e:
        print("Add contact error exception: {0}".format(e))
        print(f'Tried adding: {contact.name} <{contact.email}>')
        sys.stdout.flush()
        results.add(False)
    return all(results)

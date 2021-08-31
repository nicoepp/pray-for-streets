import json
import os
import sys

from django.contrib.auth.models import User
from django.utils.crypto import get_random_string
from mailjet_rest.client import ApiError

from sendgrid.helpers.mail import Mail, To
from sendgrid import SendGridAPIClient
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
TEMPLATE_ID = 'd-5f4bb94f40e3414a9784f9699b31e429'


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

        if not resp.status_code == 200:
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
    message = Mail(from_email=FROM_EMAIL, to_emails=[(email, name)])
    message.dynamic_template_data = {
        'email_token': token,
    }
    message.template_id = 'd-ebe70fe7eb414f329f3e2e1032707bdf'

    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sg.send(message)
        code = response.status_code
        print(f"   Consent email sent to: {name} <{email}> -- code: {code}")
        return True
    except Exception as e:
        print("   Consent email sending error: {0}".format(e))
        print(f'   Tried sending to: {name} <{email}>')
        return False


def send_street_co_subscriber_list(name, email, subscribers, street_name):
    message = Mail(from_email=FROM_EMAIL, to_emails=[(email, name)])
    message.dynamic_template_data = {
        'name': name,
        'street_name': street_name,
        'subscribers': [{'name': s[0], 'email': s[1]} for s in subscribers],  # [(name, email), (name, email)]
    }
    message.template_id = 'd-e4f88d03d5e1444cbcfdec1c2263d470'

    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sg.send(message)
        code = response.status_code
        print(f"   Subscribers list sent to: {name} <{email}> -- code: {code}")
        return True
    except Exception as e:
        print("   Subscribers list sending error: {0}".format(e))
        print(f'   Tried sending to: {name} <{email}>')
        return False


def resend_mail(from_, to, subject, text, html=''):
    staff_emails = [i[0] for i in User.objects.filter(is_staff=True).exclude(email='').values_list('email')]
    if not staff_emails:
        print('No staff users with an email listed')
        return False
    destination = 'stories' if 'stories@' in to else 'info'
    noreply = f'ANPW {destination} <noreply@prayforabbotsford.com>'
    message = Mail(from_email=noreply, to_emails=staff_emails, subject=subject, plain_text_content=text)
    if html:
        message.add_content(html, "text/html")
    message.reply_to = from_

    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sg.send(message)
        code, body, headers = response.status_code, response.body, response.headers
        print(f"Email from {from_} with subject {subject} resent. {code}")
        return True
    except Exception as e:
        print("Email resending error: {0}".format(e))
        print(f'Tried sending email from {from_} with subject {subject}')
        return False


def reminder_email(name, email, token, apikey=None, subject=None, template=None):
    from_mailgun_email = FROM_EMAIL.replace('@pray', '@m.pray')
    try:
        key = os.environ.get('MAILGUN_API_KEY', apikey)
        if not key:
            print('There is no MG API key set')
            return False
        resp = requests.post(
            "https://api.mailgun.net/v3/m.prayforabbotsford.com/messages",
            auth=("api", key),
            data={
                "from": from_mailgun_email,
                "h:Reply-To": FROM_EMAIL,
                "to": f"{name} <{email}>",
                "subject": subject or "September 27, Abbotsford Neighbourhood Prayer Walk Starts!",
                "template": template or "reminder_email",
                'h:X-Mailgun-Variables': '{"email_token": "' + token + '"}'
            }
        )
        if not resp.status_code == 200:
            print("Reminder email sending error: {0}".format(resp.status_code))
            return False
        print('Reminder email sent: ', resp.content)
        return True
    except requests.RequestException as e:
        print("Reminder email sending error: {0}".format(e))
        try:
            print(e.response.content)
        except Exception:
            pass
        return False


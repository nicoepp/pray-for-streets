import time

from django.core.management.base import BaseCommand, CommandError

from backend.streetsignup.models import Street, Contact
from backend.streetsignup.utils import reminder_email

TEMPLATE = 'reminder_email_2'
SUBJECT = ' -- 2nd Email -- '  # THIS is a TEST value !!!


class Command(BaseCommand):
    help = 'Send first email reminder (using Mailgun)'

    def add_arguments(self, parser):
        parser.add_argument('--test', default=False)

    def handle(self, *args, **options):
        emails_not_sent = set()

        for i, contact in enumerate(Contact.objects.filter(verified=True, unsubscribed=False)):
            if (i+1) % 20 == 0:
                print('-- Sleep 10 seconds --')
                time.sleep(10)
            if options['test']:
                print('test:', contact.name, contact.email)
                continue

            if not reminder_email(contact.name,
                                  contact.email,
                                  contact.verification_token,
                                  template=TEMPLATE,
                                  subject=SUBJECT):
                emails_not_sent.add(contact.email)

        if emails_not_sent:
            print('  ---   ')
            print('Emails not able to sent')
            print(emails_not_sent)

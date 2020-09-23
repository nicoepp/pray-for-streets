from django.core.management.base import BaseCommand, CommandError
from django.db import models
from django.db.models import Q

from backend.streetsignup.models import Street, Contact
from backend.streetsignup.utils import ask_for_consent_email


class Command(BaseCommand):
    help = 'Send the ask for consent email to all contacts why signed up for streets with multiple subscribers'

    def handle(self, *args, **options):
        emails = set()
        verified_true = Q(subscriptions__contact__verified=True, subscriptions__contact__unsubscribed=False)
        streets = Street.objects.annotate(subs=models.Count('subscriptions', filter=verified_true)).filter(subs__gt=1)
        for st in streets:
            subs = st.subscriptions.all()
            emails.update(sub.contact.email for sub in subs)

        for email in emails:
            contact = Contact.objects.get(email=email)

            if contact.ask_consent_email_sent:
                break
            if not contact.verified:
                break
            if contact.unsubscribed:
                break

            if ask_for_consent_email(contact.name, contact.email, contact.verification_token):
                contact.ask_consent_email_sent = True
                contact.save()

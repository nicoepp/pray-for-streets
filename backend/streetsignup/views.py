import json

from django.core.exceptions import ValidationError
from django.db.models import Count
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.views.generic import TemplateView

from backend.streetsignup.models import Street, Subscription, Contact
from backend.streetsignup.utils import recaptcha_valid, send_confirmation_mail, resend_mail, ask_for_consent_email, \
    send_street_co_subscriber_list

# Host iframe for Vue App
signup_view = never_cache(TemplateView.as_view(template_name='streetsignup/signup.html'))
map_view = never_cache(TemplateView.as_view(template_name='streetsignup/map.html'))
# Serve Vue Application
app_view = never_cache(TemplateView.as_view(template_name='app.html'))
mapapp_view = never_cache(TemplateView.as_view(template_name='mapapp.html'))
# Other pages
about_view = never_cache(TemplateView.as_view(template_name='streetsignup/other/about.html'))
stories_view = never_cache(TemplateView.as_view(template_name='streetsignup/other/stories.html'))

sitemap_view = never_cache(TemplateView.as_view(template_name='streetsignup/other/sitemap.xml'))


@never_cache
def index_view(request):
    ctx = {
        'streets_total': Street.objects.count(),
        'streets_covered': Subscription.covered_streets_count()
    }
    return render(request, 'streetsignup/index.html', ctx)


@never_cache
def media_view(request):
    return render(request, 'streetsignup/other/media.html')


def all_streets(request):
    return JsonResponse({
        'streets': list(Street.objects
                              .order_by('name')
                              .values('id', 'name', subs=Count('subscriptions')))
    })


def street_geojson(request, street_pk):
    street = get_object_or_404(Street, pk=street_pk)
    geojson_dict = street.get_geojson()
    return JsonResponse(geojson_dict)


def covered_streets(request):
    return JsonResponse(Subscription.covered_streets_geojson())


@csrf_exempt
def subscribe(request, street_pk):
    if request.method == 'POST signupclosed':  # Prevent further signup for now
        form = json.loads(request.body)

        try:
            street = Street.objects.get(pk=street_pk)
            if not street.name == form.get('street_name', ''):
                return JsonResponse({'success': False, 'street_name': 'Street name is not correct'}, status=400)
            subs = Subscription(
                street=street,
                name=form.get('name', ''),
                church=form.get('church', ''),
            )
            contacts = Contact.objects.filter(email=form.get('email', ''))
            if not contacts.exists():
                contact = Contact(name=form.get('name', ''), email=form.get('email', ''))
                contact.full_clean()  # can throw ValidationError
                contact.save()
            else:
                contact = contacts.first()
            subs.contact = contact
            subs.full_clean()  # can throw ValidationError
            if not recaptcha_valid(form.get('token', '')):
                return JsonResponse({'success': False, 'token': 'reCAPTCHA invalid'}, status=400)
            resp = send_confirmation_mail(subs.name,
                                          contact.email,
                                          street_name=street.name,
                                          token=contact.verification_token)
            if resp:
                subs.save()
                return JsonResponse({'success': True, 'subscription_id': subs.pk})
            else:
                # Delete subscription or mark confirmation as unsent
                return JsonResponse({'success': False, 'email': "Couldn't send confirmation email"}, status=500)
        except Street.DoesNotExist as e:
            return JsonResponse({'success': False, 'street_id': 'Street does not exist'}, status=400)
        except ValidationError as e:
            resp = e.message_dict
            resp['success'] = False
            return JsonResponse(resp, status=400)

    return JsonResponse({'success': False}, status=404)


@csrf_exempt
@require_POST
def receive_email(request):
    # Add basic auth security here
    if request.method == 'POST':
        to = request.POST.get('to', '')
        from_ = request.POST.get('from')
        subject = request.POST.get('subject', '')
        text = request.POST.get('text', '')
        html = request.POST.get('html', '')

        if to in ['info@prayforabbotsford.com', 'stories@prayforabbotsford.com'] or '<info@' in to:
            if not resend_mail(from_, to, subject, text, html):
                return HttpResponse(status=500)

        print('--- Email from SendGrid ---')
        print('From:', from_)
        print('To:', to)
        print('Subject:', subject)
    return HttpResponse(status=200)


def verify_email(request, token):
    all_subs = Subscription.objects.filter(verification_token=token)
    all_contacts = Contact.objects.filter(verification_token=token)
    success = all_contacts.exists() or all_subs.exists()
    if success:
        contact = all_contacts.first() if all_contacts.exists() else all_subs.first().contact
        if not contact.verified:
            contact.verified = True
            contact.save()

            # If has streets with multiple subscribers (which hadn't multiple before)
            # then ask_for_consent to all subscribers who haven't given their consent yet
            # including this contact himself.
            for contact_sub in contact.subscriptions.all():
                street = contact_sub.street
                street_subs = street.subscriptions.filter(contact__verified=True, contact__unsubscribed=False)
                if street_subs.count() > 1:  # or just at equal two?
                    for sub in street_subs:
                        ct = sub.contact
                        if not ct.sharing_consent and not ct.ask_consent_email_sent:
                            if ask_for_consent_email(ct.name, ct.email, ct.verification_token):
                                ct.ask_consent_email_sent = True
                                ct.save()
    return render(request, 'streetsignup/email/verify.html', {'success': success})


def unsubscribe_email(request, token):
    all_subs = Subscription.objects.filter(verification_token=token)
    all_contacts = Contact.objects.filter(verification_token=token)
    success = all_contacts.exists() or all_subs.exists()
    if success:
        contact = all_contacts.first() if all_contacts.exists() else all_subs.first().contact
        contact.unsubscribed = True
        contact.save()
    return render(request, 'streetsignup/email/unsubscribe.html', {'success': success})


def consent_sharing_email(request, token):
    all_contacts = Contact.objects.filter(verification_token=token)
    success = all_contacts.exists()
    if success:
        contact = all_contacts.first()
        if not contact.sharing_consent:
            contact.sharing_consent = True
            contact.save()
            # If 2 shared consent (1 other) send list of subscribers to both, if 3 shared do it too (2 other)
            # Omit this one was the first (1 shared consent, no other)
            for contact_sub in contact.subscriptions.all():
                street = contact_sub.street
                street_subs = street.subscriptions.filter(contact__sharing_consent=True)
                if street_subs.count() > 1:
                    for sub in street_subs:
                        ct = sub.contact
                        emails = street_subs.exclude(contact=ct).values_list('contact__name', 'contact__email')
                        send_street_co_subscriber_list(ct.name, ct.email, emails, street_name=street.name)
    return render(request, 'streetsignup/email/consent.html', {'success': success})

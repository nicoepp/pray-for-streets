import json

from django.core.exceptions import ValidationError
from django.db.models import Count
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse, HttpRequest
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.views.generic import TemplateView

from backend.streetsignup.models import Street, Subscription, Contact, City
from backend.streetsignup.utils import recaptcha_valid, send_confirmation_mail, ask_for_consent_email, \
    send_street_co_subscriber_list, add_to_mailjet
from backend.pages.models import HomePage
from wagtail.core.models import Site

# Host iframe for Vue App
signup_view = never_cache(TemplateView.as_view(template_name='streetsignup/signup.html'))
map_view = never_cache(TemplateView.as_view(template_name='streetsignup/map.html'))
# Serve Vue Application
app_view = never_cache(TemplateView.as_view(template_name='app.html'))
mapapp_view = never_cache(TemplateView.as_view(template_name='mapapp.html'))
# Other pages
about_view = never_cache(TemplateView.as_view(template_name='streetsignup/other/about.html'))
stories_view = never_cache(TemplateView.as_view(template_name='streetsignup/other/stories.html'))


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


def all_streets(request, site_name):
    print('We are in: ' + site_name)

    root_page = Site.objects.filter(hostname=site_name).first().root_page
    city = HomePage.objects.filter(pk=root_page.pk).first().city

    return JsonResponse({
        'streets': list(Street.objects
                              .filter(city_site=city)
                              .order_by('name')
                              .values('id', 'name', subs=Count('subscriptions')))
    })


def street_geojson(request, street_pk):
    street = get_object_or_404(Street, pk=street_pk)
    geojson_dict = street.get_geojson()
    return JsonResponse(geojson_dict)


def covered_streets(request):
    hostname = request.GET.get('site', None)
    return JsonResponse(Subscription.covered_streets_geojson(hostname))


def all_streets_per_city(request):
    hostname = request.GET.get('site', None)
    return JsonResponse(Street.all_streets_geojson(hostname))


@csrf_exempt
def subscribe(request, street_pk):
    if request.method == 'POST':
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
            city = street.city_site
            resp = send_confirmation_mail(subs.name,
                                          contact.email,
                                          street_name=street.name,
                                          token=contact.verification_token,
                                          city=city)
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


def verify_email(request, token):
    all_subs = Subscription.objects.filter(verification_token=token)
    all_contacts = Contact.objects.filter(verification_token=token)
    success = all_contacts.exists() or all_subs.exists()
    if success:
        contact = all_contacts.first() if all_contacts.exists() else all_subs.first().contact
        if not contact.verified:
            contact.verified = True

            # Add to corresponding subscriber list
            cities = City.objects.filter(street__subscriptions__contact=contact)
            success = add_to_mailjet(contact, cities)
            if not success:
                contact.verified = False
            contact.save()

            # If has streets with multiple subscribers (which hadn't multiple before)
            # then ask_for_consent to all subscribers who haven't given their consent yet
            # including this contact himself.
            for contact_sub in contact.subscriptions.all():
                street = contact_sub.street
                street_subs = street.subscriptions.filter(contact__verified=True, contact__unsubscribed=False)
                if street_subs.count() > 1:  # or just at equal two?
                    for sub in street_subs:               # We should hook up to unsub events and update DB accordingly
                        ct = sub.contact                  # before sending out these sharing consent emails
                        if not ct.sharing_consent and not ct.ask_consent_email_sent and False:
                            if ask_for_consent_email(ct.name, ct.email, ct.verification_token):
                                ct.ask_consent_email_sent = True
                                ct.save()

    return render(request, 'streetsignup/email/verify.html', {'success': success, 'bg_img': get_bg_image(request)})


def unsubscribe_email(request, token):
    all_subs = Subscription.objects.filter(verification_token=token)
    all_contacts = Contact.objects.filter(verification_token=token)
    success = all_contacts.exists() or all_subs.exists()
    if success:
        contact = all_contacts.first() if all_contacts.exists() else all_subs.first().contact
        contact.unsubscribed = True
        contact.save()
    return render(request, 'streetsignup/email/unsubscribe.html', {'success': success, 'bg_img': get_bg_image(request)})


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
    return render(request, 'streetsignup/email/consent.html', {'success': success, 'bg_img': get_bg_image(request)})


def get_bg_image(request: HttpRequest):
    host = request.get_host()
    if not host:
        return None

    sites = Site.objects.filter(hostname=host.split(':')[0])

    if sites.exists():
        root_page = sites.first().root_page
        return HomePage.objects.filter(pk=root_page.pk).first().background_image
    return None

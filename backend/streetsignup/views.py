import json

from django.core.exceptions import ValidationError
from django.db.models import Count
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.views.generic import TemplateView

from backend.streetsignup.models import Street, Subscription
from backend.streetsignup.utils import recaptcha_valid, send_confirmation_mail, resend_mail

# Host iframe for Vue App
signup_view = never_cache(TemplateView.as_view(template_name='streetsignup/signup.html'))
map_view = never_cache(TemplateView.as_view(template_name='streetsignup/map.html'))
# Serve Vue Application
app_view = never_cache(TemplateView.as_view(template_name='app.html'))
mapapp_view = never_cache(TemplateView.as_view(template_name='mapapp.html'))
# Other pages
about_view = never_cache(TemplateView.as_view(template_name='streetsignup/other/about.html'))
media_view = never_cache(TemplateView.as_view(template_name='streetsignup/other/media.html'))
stories_view = never_cache(TemplateView.as_view(template_name='streetsignup/other/stories.html'))


@never_cache
def index_view(request):
    ctx = {
        'streets_total': Street.objects.count(),
        'streets_covered': Subscription.covered_streets_count()
    }
    return render(request, 'streetsignup/index.html', ctx)


def all_streets(request):
    return JsonResponse({
        'streets': list(Street.objects
                              .order_by('name')
                              .values('id', 'name', subs=Count('subscription')))
    })


def street_geojson(request, street_pk):
    street = get_object_or_404(Street, pk=street_pk)
    geojson_dict = street.get_geojson()
    return JsonResponse(geojson_dict)


def covered_streets(request):
    return JsonResponse(Subscription.covered_streets_geojson())


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
                email=form.get('email', ''),
                church=form.get('church', ''),
            )
            subs.full_clean()  # can throw ValidationError
            if not recaptcha_valid(form.get('token', '')):
                return JsonResponse({'success': False, 'token': 'reCAPTCHA invalid'}, status=400)
            subs.save()
            resp = send_confirmation_mail(subs.name, subs.email, street_name=street.name, token=subs.verification_token)
            if resp:
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
    if request.method == 'POST':
        to = request.POST.get('to', '')
        if to in ['info@prayforabbotsford.com', 'stories@prayforabbotsford.com'] or '<info@' in to:
            if not resend_mail(request.POST.get('from'), to, request.POST.get('subject'), request.POST.get('text')):
                return HttpResponse(status=500)
        print('--- Email from SendGrid ---')
        print('From:', request.POST.get('from'))
        print('To:', request.POST.get('to'))
        print('Subject:', request.POST.get('subject'))
        print('Body:', request.POST.get('text'))
        print('Html:', request.POST.get('html'))
    return HttpResponse(status=200)


def verify_email(request, token):
    all_subs = Subscription.objects.filter(verification_token=token)
    success = all_subs.exists()
    if success:
        sub = all_subs.first()
        sub.verified = True
        sub.save()
    return render(request, 'streetsignup/email/verify.html', {'success': success})


def unsubscribe_email(request, token):
    all_subs = Subscription.objects.filter(verification_token=token)
    success = all_subs.exists()
    street_name = ''
    if success:
        sub = all_subs.first()
        sub.unsubscribed = True
        sub.save()
        street_name = sub.street.name
    return render(request, 'streetsignup/email/unsubscribe.html', {'success': success, 'street_name': street_name})

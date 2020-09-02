import json

from django.core.exceptions import ValidationError
from django.db.models import Count
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView

from backend.streetsignup.models import Street, Subscription
from backend.streetsignup.utils import recaptcha_valid

# Serve Vue Application
index_view = never_cache(TemplateView.as_view(template_name='streetsignup/index.html'))
signup_view = never_cache(TemplateView.as_view(template_name='streetsignup/signup.html'))
map_view = never_cache(TemplateView.as_view(template_name='streetsignup/map.html'))
app_view = never_cache(TemplateView.as_view(template_name='app.html'))
mapapp_view = never_cache(TemplateView.as_view(template_name='mapapp.html'))


def all_streets(request):
    return JsonResponse({'streets': list(Street.objects.values('id', 'name', subs=Count('subscription')))})


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
            return JsonResponse({'success': True, 'subscription_id': subs.pk})
        except Street.DoesNotExist as e:
            return JsonResponse({'success': False, 'street_id': 'Street does not exist'}, status=400)
        except ValidationError as e:
            resp = e.message_dict
            resp['success'] = False
            return JsonResponse(resp, status=400)

    return JsonResponse({'success': False}, status=404)

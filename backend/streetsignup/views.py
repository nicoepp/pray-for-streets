from django.db.models import Count
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.views.decorators.cache import never_cache
from django.views.generic import TemplateView

from backend.streetsignup.models import Street, Subscription

# Serve Vue Application
index_view = never_cache(TemplateView.as_view(template_name='index.html'))


def all_streets(request):
    return JsonResponse({'streets': list(Street.objects.values('id', 'name', subs=Count('subscription')))})


def street_geojson(request, street_pk):
    street = get_object_or_404(Street, pk=street_pk)
    geojson_dict = street.get_geojson()
    return JsonResponse(geojson_dict)


def covered_streets(request):
    return JsonResponse(Subscription.covered_streets_geojson())

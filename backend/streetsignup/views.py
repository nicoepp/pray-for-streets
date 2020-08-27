from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.cache import never_cache
from django.views.generic import TemplateView

STREETS = ['MT LEHMAN RD', 'HAMM RD', 'TOWNLINE RD', 'CLEARBROOK RD', 'LAXTON ST', 'COLUMBIA ST', 'MONTGOMERY AVE',
           'GLADWIN RD', 'MCCALLUM RD', 'SHORT RD', 'FARMER RD', 'MCKENZIE RD']

# Serve Vue Application
index_view = never_cache(TemplateView.as_view(template_name='index.html'))


def subscriptions(request):
    return JsonResponse({'subscriptions': STREETS})

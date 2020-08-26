from django.shortcuts import render
from django.http import HttpResponse, JsonResponse

STREETS = ['MT LEHMAN RD', 'HAMM RD', 'TOWNLINE RD', 'CLEARBROOK RD', 'LAXTON ST', 'COLUMBIA ST', 'MONTGOMERY AVE',
           'GLADWIN RD', 'MCCALLUM RD', 'SHORT RD', 'FARMER RD', 'MCKENZIE RD']


def index(request):
    return HttpResponse("Hello, world. You're at the SignUp index.")


def subscriptions(request):
    return JsonResponse({'subscriptions': STREETS})

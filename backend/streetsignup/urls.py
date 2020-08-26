from django.urls import path

from . import views

urlpatterns = [
    path('api/subscriptions', views.subscriptions, name='subscriptions'),
    path('', views.index, name='index'),
]

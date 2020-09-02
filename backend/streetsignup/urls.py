from django.urls import path

from . import views

urlpatterns = [
    path('api/streets/<int:street_pk>.geo.json', views.street_geojson, name='street_geojson'),
    path('api/streets/covered_streets.geo.json', views.covered_streets, name='covered_streets'),
    path('api/streets/<int:street_pk>/subscribe', views.subscribe, name='subscribe'),
    path('api/streets', views.all_streets, name='all_streets'),
    path('', views.index_view, name='index'),
    path('', views.signup_view, name='signup'),
]

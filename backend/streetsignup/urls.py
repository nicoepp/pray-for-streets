from django.urls import path

from . import views

api_urlpatterns = [
    path('streets/<int:street_pk>.geo.json', views.street_geojson, name='street_geojson'),
    path('streets/covered_streets.geo.json', views.covered_streets, name='covered_streets'),
    path('streets/<int:street_pk>/subscribe', views.subscribe, name='subscribe'),
    path('streets', views.all_streets, name='all_streets'),
]

embed_urlpatterns = [
    path('app', views.app_view, name='app'),              # Vue
    path('mapapp', views.mapapp_view, name='mapapp'),     # "
]

email_urlpatterns = [
    path('inbound', views.receive_email, name='email'),
    path('confirm/<token>', views.verify_email, name='verify_email'),
    path('unsubscribe/<token>', views.unsubscribe_email, name='unsubscribe'),
    path('consent_to_share/<token>', views.consent_sharing_email, name='consent'),
]

from django.urls import path

from . import views

urlpatterns = [
    path('api/streets/<int:street_pk>.geo.json', views.street_geojson, name='street_geojson'),
    path('api/streets/covered_streets.geo.json', views.covered_streets, name='covered_streets'),
    path('api/streets/<int:street_pk>/subscribe', views.subscribe, name='subscribe'),
    path('api/streets', views.all_streets, name='all_streets'),
    path('app', views.app_view, name='app'),              # Vue
    path('mapapp', views.mapapp_view, name='mapapp'),     # "
    path('signup', views.signup_view, name='signup'),     # IFrame
    path('map', views.map_view, name='map'),              # "
    path('about', views.about_view, name='about'),        # Other
    path('media', views.media_view, name='media'),        # "
    path('stories', views.stories_view, name='stories'),  # "
    path('inbound_email', views.receive_email, name='email'),
    path('', views.index_view, name='index'),
]

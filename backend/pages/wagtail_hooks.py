from django.db.models import QuerySet
from django.http import HttpRequest
from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register

from backend.streetsignup.models import Subscription, City


def contact_verified(obj):
    return obj.contact.verified


contact_verified.short_description = 'Verified'
contact_verified.boolean = True


@modeladmin_register
class SubscriptionAdmin(ModelAdmin):
    model = Subscription
    menu_icon = 'tasks'
    search_fields = ['street__name', 'name', 'church']
    list_display = ['name', 'church', 'street', 'created_at', contact_verified]

    def get_queryset(self, request: HttpRequest):
        qs: QuerySet = super().get_queryset(request)

        groups = request.user.groups.all()

        return qs.filter(street__city_site__group__in=groups)


def site_host(obj) -> str:
    if not obj.homepage.exists():
        return '---'
    return obj.homepage.first().get_site().hostname


@modeladmin_register
class CityAdmin(ModelAdmin):
    model = City
    menu_icon = 'home'
    list_display = ['name', 'province', site_host, 'group']

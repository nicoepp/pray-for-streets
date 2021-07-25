from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register

from backend.streetsignup.models import Subscription


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

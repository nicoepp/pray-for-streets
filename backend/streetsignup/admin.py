from django.contrib import admin
from .models import Subscription


def contact_verified(obj):
    return obj.contact.verified


contact_verified.short_description = 'Verified'
contact_verified.boolean = True


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    # exclude_fields and readonly_fields
    search_fields = ['street__name', 'name', 'church']
    list_display = ['name', 'church', 'street', 'created_at', contact_verified]

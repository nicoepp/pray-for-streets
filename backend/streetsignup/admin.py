from django.contrib import admin
from .models import Subscription


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    search_fields = ['street__name', 'name', 'church']
    list_display = ['name', 'church', 'street', 'created_at', 'verified']

from django.contrib.auth.models import Group
from django.db import models
from wagtail.admin.edit_handlers import FieldPanel
from wagtail.core.models import Site

from .utils import segments_to_geojson, get_email_token


class City(models.Model):
    name = models.CharField(max_length=80)
    province = models.CharField(max_length=80)
    group = models.OneToOneField(Group, null=True, blank=True, on_delete=models.PROTECT)

    def __str__(self):
        return f'{self.name}, {self.province}'

    class Meta:
        verbose_name_plural = 'cities'


class Street(models.Model):
    name = models.CharField(max_length=80)
    city_site = models.ForeignKey(City, on_delete=models.CASCADE)

    def get_geojson(self):
        """ Returns a dict in GeoJSON format """
        return segments_to_geojson(self.segments.values('pk', 'path'), self.name)

    def __str__(self):
        return self.name


class Segment(models.Model):
    street = models.ForeignKey(Street, related_name='segments', on_delete=models.CASCADE)
    objectid = models.IntegerField(null=True)
    path = models.JSONField()

    def __str__(self):
        return f'Segment {self.objectid} - {self.street}'


class Contact(models.Model):
    name = models.CharField(max_length=30)
    email = models.EmailField(unique=True, db_index=True)

    verification_token = models.SlugField(db_index=True, default=get_email_token)
    verified = models.BooleanField(default=False)
    unsubscribed = models.BooleanField(default=False)
    sharing_consent = models.BooleanField(default=False)
    ask_consent_email_sent = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.name[:8]} <{self.email}>'


class Subscription(models.Model):
    street = models.ForeignKey(Street, related_name='subscriptions', on_delete=models.PROTECT)  # Look for Count('sub..
    name = models.CharField(max_length=30)
    contact = models.ForeignKey(Contact, null=True, related_name='subscriptions', on_delete=models.PROTECT)
    church = models.CharField(max_length=40)

    verification_token = models.SlugField(db_index=True, default=get_email_token)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    panels = [
        FieldPanel('street'),
        FieldPanel('name'),
        FieldPanel('contact'),
        FieldPanel('church'),
    ]

    def __str__(self):
        return f'{self.name}, {self.church}: {self.street.name}'

    @staticmethod
    def covered_streets_geojson(hostname=None):
        segments = Segment.objects.annotate(subs=models.Count('street__subscriptions')).filter(subs__gt=0)
        if hostname:
            sites = Site.objects.filter(hostname=hostname)
            if sites.exists():
                homepage = sites.first().root_page
                segments = segments.filter(street__city_site__homepage=homepage)

        return segments_to_geojson(segments.values('pk', 'path', 'street__name'))

    @staticmethod
    def covered_streets_count():
        return Street.objects.annotate(subs=models.Count('subscriptions')).filter(subs__gt=0).count()

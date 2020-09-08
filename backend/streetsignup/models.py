from django.db import models
from .utils import segments_to_geojson, get_email_token


class Street(models.Model):
    name = models.CharField(max_length=80)

    def get_geojson(self):
        """ Returns a dict in GeoJSON format """
        return segments_to_geojson(self.segments.values('pk', 'path'), self.name)

    def __str__(self):
        return self.name


class Segment(models.Model):
    street = models.ForeignKey(Street, related_name='segments', on_delete=models.CASCADE)
    objectid = models.IntegerField(unique=True, db_index=True)
    path = models.JSONField()

    def __str__(self):
        return f'Segment {self.objectid} - {self.street}'


class Subscription(models.Model):
    street = models.ForeignKey(Street, on_delete=models.PROTECT)
    name = models.CharField(max_length=30)
    email = models.EmailField()
    church = models.CharField(max_length=40)

    verification_token = models.SlugField(db_index=True, default=get_email_token)
    verified = models.BooleanField(default=False)
    unsubscribed = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.name}, {self.church}: {self.street.name}'

    @staticmethod
    def covered_streets_geojson():
        segments = Segment.objects.annotate(subs=models.Count('street__subscription')).filter(subs__gt=0)
        return segments_to_geojson(segments.values('pk', 'path', 'street__name'))

    @staticmethod
    def covered_streets_count():
        return Street.objects.annotate(subs=models.Count('subscription')).filter(subs__gt=0).count()

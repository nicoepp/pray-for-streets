from django.db import models


class Street(models.Model):
    name = models.CharField(max_length=80)

    def get_geojson(self):
        """ Returns a dict in GeoJSON format """
        features = []
        for segment in self.segments.all():
            features.append({
                'id': segment.pk,
                'type': "Feature",
                'properties': {
                    'STREET_NAME': self.name
                },
                'geometry': {
                    'type': 'LineString',
                    'coordinates': segment.path if segment.path else []
                }
            })

        return {
          "type": "FeatureCollection",
          "features": features,
        }


class Segment(models.Model):
    street = models.ForeignKey(Street, related_name='segments', on_delete=models.CASCADE)
    objectid = models.IntegerField(unique=True, db_index=True)
    path = models.JSONField()


class Subscription(models.Model):
    street = models.ForeignKey(Street, null=True, on_delete=models.PROTECT)
    name = models.CharField(max_length=30)
    email = models.EmailField()
    church = models.CharField(max_length=40)

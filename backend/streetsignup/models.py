from django.db import models


class Street(models.Model):
    name = models.CharField(max_length=80)


class Segment(models.Model):
    street = models.ForeignKey(Street, on_delete=models.CASCADE)
    objectid = models.IntegerField(unique=True, db_index=True)
    path = models.JSONField()


class Subscription(models.Model):
    street = models.ForeignKey(Street, null=True, on_delete=models.PROTECT)
    name = models.CharField(max_length=30)
    email = models.EmailField()
    church = models.CharField(max_length=40)

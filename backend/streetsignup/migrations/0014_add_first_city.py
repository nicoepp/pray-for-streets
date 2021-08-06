
from django.db import migrations


def add_city(apps, schema_editor):
    # We can't import the Subscription model directly as it may be a newer
    # version than this migration expects. We use the historical version.
    City = apps.get_model('streetsignup', 'City')
    Street = apps.get_model('streetsignup', 'Street')

    if not City.objects.exists():
        city = City(name='Abbotsford', province='British Columbia', site='prayforabbotsford.com')
        city.save()

    cities = City.objects.filter(name__startswith='Abbotsford')

    if not cities.exists():
        cities = City.objects.all()

    city = cities.first()

    for street in Street.objects.all():
        street.city_site = city
        street.save()


def backward(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('streetsignup', '0013_rename_city_city_name'),
    ]

    operations = [
        migrations.RunPython(add_city, backward),
    ]

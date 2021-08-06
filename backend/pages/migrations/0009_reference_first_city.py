
from django.db import migrations


def reference_city(apps, schema_editor):
    # We can't import the Subscription model directly as it may be a newer
    # version than this migration expects. We use the historical version.
    City = apps.get_model('streetsignup', 'City')
    HomePage = apps.get_model('pages', 'HomePage')

    cities = City.objects.filter(name__startswith='Abbotsford')

    if not cities.exists():
        cities = City.objects.all()

    city = cities.first()

    for page in HomePage.objects.all():
        page.city = city
        page.save()


def backward(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0008_homepage_city'),
        ('streetsignup', '0014_add_first_city'),
    ]

    operations = [
        migrations.RunPython(reference_city, backward),
    ]

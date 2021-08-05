# Generated by Django 3.2.6 on 2021-08-05 05:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('streetsignup', '0012_street_city_site'),
        ('pages', '0007_menupage_icon'),
    ]

    operations = [
        migrations.AddField(
            model_name='homepage',
            name='city',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, to='streetsignup.city'),
            preserve_default=False,
        ),
    ]

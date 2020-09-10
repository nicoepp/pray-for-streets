# Generated by Django 3.1.1 on 2020-09-08 22:06

import backend.streetsignup.utils
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('streetsignup', '0003_auto_20200901_2308'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscription',
            name='unsubscribed',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='subscription',
            name='verification_token',
            field=models.SlugField(default=backend.streetsignup.utils.get_email_token),
        ),
        migrations.AddField(
            model_name='subscription',
            name='verified',
            field=models.BooleanField(default=False),
        ),
    ]
# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-07-16 13:04
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('applicationManager', '0013_datadump'),
    ]

    operations = [
        migrations.AddField(
            model_name='application',
            name='coming_soon_page',
            field=models.BooleanField(default=True),
        ),
    ]

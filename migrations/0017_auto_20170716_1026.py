# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-07-16 15:26
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('applicationManager', '0016_auto_20170716_1022'),
    ]

    operations = [
        migrations.AlterField(
            model_name='application',
            name='uuid',
            field=models.UUIDField(blank=True, null=True),
        ),
    ]

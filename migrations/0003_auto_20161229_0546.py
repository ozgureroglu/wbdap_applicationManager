# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2016-12-29 11:46
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('applicationManager', '0002_auto_20161229_0511'),
    ]

    operations = [
        migrations.RenameField(
            model_name='application',
            old_name='models',
            new_name='model',
        ),
    ]

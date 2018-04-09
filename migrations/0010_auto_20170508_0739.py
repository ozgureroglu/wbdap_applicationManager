# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-08 12:39
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('applicationManager', '0009_auto_20170508_0713'),
    ]

    operations = [
        migrations.RenameField(
            model_name='application',
            old_name='appName',
            new_name='app_name',
        ),
        migrations.AlterField(
            model_name='field',
            name='model',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='fields', to='applicationManager.Model'),
        ),
    ]

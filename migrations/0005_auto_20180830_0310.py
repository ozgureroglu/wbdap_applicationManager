# Generated by Django 2.0.8 on 2018-08-30 08:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('applicationManager', '0004_auto_20180830_0309'),
    ]

    operations = [
        migrations.AlterField(
            model_name='applicationcomponenttemplate',
            name='definition',
            field=models.TextField(default=None, max_length=200),
        ),
    ]
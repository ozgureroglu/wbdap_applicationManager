# Generated by Django 2.0.2 on 2018-02-27 19:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('applicationManager', '0023_model_definition'),
    ]

    operations = [
        migrations.AlterField(
            model_name='model',
            name='definition',
            field=models.TextField(blank=True, max_length=250, null=True),
        ),
    ]
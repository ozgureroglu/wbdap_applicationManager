# Generated by Django 2.2.4 on 2019-09-04 10:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('applicationManager', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='applicationlayout',
            name='description',
            field=models.TextField(blank=True, max_length=200, null=True),
        ),
    ]
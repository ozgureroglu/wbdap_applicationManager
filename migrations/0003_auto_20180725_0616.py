# Generated by Django 2.0.7 on 2018-07-25 11:16

import ckeditor.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('applicationManager', '0002_auto_20180720_1401'),
    ]

    operations = [
        migrations.CreateModel(
            name='ApplicationPage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('page_name', models.CharField(max_length=25)),
                ('app', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='pages', to='applicationManager.Application')),
            ],
        ),
        migrations.CreateModel(
            name='PageLayout',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('layout_name', models.CharField(max_length=25)),
                ('content', ckeditor.fields.RichTextField()),
            ],
        ),
        migrations.AddField(
            model_name='applicationpage',
            name='page_layout',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='applicationManager.PageLayout'),
        ),
    ]

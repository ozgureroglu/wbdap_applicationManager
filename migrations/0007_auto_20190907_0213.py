# Generated by Django 2.2.4 on 2019-09-07 07:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('applicationManager', '0006_auto_20190907_0200'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='application',
            name='coming_soon_page',
        ),
        migrations.CreateModel(
            name='ApplicationDefaultPages',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('coming_soon_page', models.BooleanField(default=True)),
                ('about_us_page', models.BooleanField(default=True)),
                ('contact_us_page', models.BooleanField(default=True)),
                ('landing_page', models.BooleanField(default=True)),
                ('maintenance_page', models.BooleanField(default=True)),
                ('app', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='applicationManager.Application')),
            ],
        ),
    ]

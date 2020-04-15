# Generated by Django 3.0.4 on 2020-04-03 07:04

import ckeditor.fields
from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import re


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Application',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('app_name', models.CharField(max_length=25)),
                ('verbose_name', models.CharField(max_length=50)),
                ('url', models.CharField(max_length=30)),
                ('namedUrl', models.CharField(max_length=30)),
                ('description', models.TextField(default='A brief explanation of this application.', max_length=500)),
                ('active', models.BooleanField(blank=True, default=True)),
                ('core_app', models.BooleanField(default=False)),
                ('uuid', models.UUIDField(blank=True, null=True)),
                ('published', models.BooleanField(default=False)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'permissions': (('has_access', 'Has access to application pages'),),
            },
        ),
        migrations.CreateModel(
            name='ApplicationComponentTemplate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('temp_name', models.CharField(blank=True, max_length=50, null=True)),
                ('temp_type', models.CharField(choices=[('generic', 'Generic Purpose Template'), ('view', 'View Template'), ('url', 'URL Template'), ('html', 'HTML file Template'), ('license', 'License File Template'), ('python', 'Python File Template')], default='generic', max_length=60)),
                ('temp_content', models.TextField(blank=True, default=None, max_length=5000, null=True)),
                ('temp_engine', models.CharField(choices=[('django', 'Django Template'), ('jinja2', 'Jinja2 Template'), ('mako', 'Mako Template'), ('mustache', 'Mustache Template')], default='django', max_length=60)),
                ('definition', models.TextField(blank=True, default=None, max_length=200)),
            ],
            options={
                'unique_together': {('temp_name', 'temp_type')},
            },
        ),
        migrations.CreateModel(
            name='ApplicationLayout',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('description', models.TextField(blank=True, max_length=200, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='AppModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('definition', models.TextField(blank=True, max_length=250)),
                ('owner_app', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='models', to='applicationManager.Application')),
            ],
        ),
        migrations.CreateModel(
            name='DjangoProject',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=25)),
                ('port', models.IntegerField(validators=[django.core.validators.MaxValueValidator(10000), django.core.validators.MinValueValidator(1000)])),
                ('status', models.BooleanField(default=False)),
                ('description', models.TextField(max_length=400)),
                ('pids', models.CharField(max_length=50, null=True, validators=[django.core.validators.RegexValidator(re.compile('^\\d+(?:\\,\\d+)*\\Z'), code='invalid', message='Enter only digits separated by commas.')])),
                ('sample_app', models.BooleanField(default=True, verbose_name='Create Sample Application')),
                ('enable_messages', models.BooleanField(default=True, verbose_name='Enable Messages Framework for Application')),
                ('enable_drf_api', models.BooleanField(default=True, verbose_name='Enable DRF for Application')),
            ],
        ),
        migrations.CreateModel(
            name='PageLayout',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('layout_name', models.CharField(max_length=25)),
                ('layout_description', models.TextField(blank=True, max_length=250, null=True)),
                ('layout_icon_name', models.CharField(blank=True, max_length=50, null=True)),
                ('layout_template_code', ckeditor.fields.RichTextField()),
            ],
        ),
        migrations.CreateModel(
            name='PasswordSetting',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('minLength', models.IntegerField()),
                ('maxLength', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='SettingDefinition',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default=None, max_length=30)),
                ('verbose_name', models.CharField(default=None, max_length=60)),
                ('definition', models.CharField(default=None, max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='DataDump',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('application', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='applicationManager.Application')),
            ],
        ),
        migrations.CreateModel(
            name='AppModelField',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('field_type', models.CharField(choices=[('AutoField', 'AutoField'), ('BLANK_CHOICE_DASH', 'BLANK_CHOICE_DASH'), ('BigAutoField', 'BigAutoField'), ('BigIntegerField', 'BigIntegerField'), ('BinaryField', 'BinaryField'), ('BooleanField', 'BooleanField'), ('CharField', 'CharField'), ('CommaSeparatedIntegerField', 'CommaSeparatedIntegerField'), ('DateField', 'DateField'), ('DateTimeField', 'DateTimeField'), ('DecimalField', 'DecimalField'), ('DurationField', 'DurationField'), ('EmailField', 'EmailField'), ('Empty', 'Empty'), ('Field', 'Field'), ('FieldDoesNotExist', 'FieldDoesNotExist'), ('FilePathField', 'FilePathField'), ('FloatField', 'FloatField'), ('GenericIPAddressField', 'GenericIPAddressField'), ('IPAddressField', 'IPAddressField'), ('IntegerField', 'IntegerField'), ('NOT_PROVIDED', 'NOT_PROVIDED'), ('NullBooleanField', 'NullBooleanField'), ('PositiveIntegerField', 'PositiveIntegerField'), ('PositiveSmallIntegerField', 'PositiveSmallIntegerField'), ('SlugField', 'SlugField'), ('SmallAutoField', 'SmallAutoField'), ('SmallIntegerField', 'SmallIntegerField'), ('TextField', 'TextField'), ('TimeField', 'TimeField'), ('URLField', 'URLField'), ('UUIDField', 'UUIDField')], max_length=30)),
                ('type_parameter', models.TextField(blank=True, max_length=150, null=True)),
                ('definition', models.TextField(blank=True, max_length=250)),
                ('verbose_name', models.CharField(default='vname', max_length=40)),
                ('primary_key', models.BooleanField(default=False)),
                ('max_length', models.IntegerField(default=50)),
                ('unique', models.BooleanField(default=False)),
                ('blank', models.BooleanField(default=False)),
                ('null', models.BooleanField(default=False)),
                ('db_index', models.BooleanField(default=False)),
                ('rel', models.CharField(default=None, max_length=50)),
                ('default', models.CharField(max_length=50)),
                ('editable', models.BooleanField(default=True)),
                ('serialize', models.BooleanField(default=True)),
                ('auto_created', models.BooleanField(default=False)),
                ('owner_model', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='fields', to='applicationManager.AppModel')),
            ],
        ),
        migrations.CreateModel(
            name='ApplicationView',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('view_name', models.CharField(blank=True, max_length=50, null=True)),
                ('view_type', models.CharField(choices=[('ordinary', 'Bare Python Function'), ('class_based', 'Generic Class Based Django View')], default='ordinary', max_length=50)),
                ('view_code', models.TextField(blank=True, default=None, max_length=500, null=True)),
                ('return_type', models.CharField(choices=[('ordinary', 'Bare Python Function'), ('class_based', 'Generic Class Based Django View')], default='ordinary', max_length=50)),
                ('app', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='views', to='applicationManager.Application')),
                ('template', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='applicationManager.ApplicationComponentTemplate')),
            ],
        ),
        migrations.CreateModel(
            name='ApplicationUrl',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url_pattern', models.CharField(blank=True, max_length=50, null=True)),
                ('url_name', models.CharField(blank=True, max_length=50, null=True)),
                ('app', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='paths', to='applicationManager.Application')),
                ('view_method', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mapped_view', to='applicationManager.ApplicationView')),
            ],
        ),
        migrations.CreateModel(
            name='ApplicationPage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('page_type', models.CharField(choices=[('predefined', 'Predefined Template'), ('empty', 'Empty Page'), ('landing', 'Landing Page'), ('index', 'Application Index Page'), ('about', 'About Page'), ('contact', 'Contact Page')], default='predefined', max_length=25)),
                ('page_name', models.CharField(max_length=25)),
                ('app', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='pages', to='applicationManager.Application')),
                ('page_layout', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='applicationManager.PageLayout')),
            ],
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
        migrations.CreateModel(
            name='ApplicationSettings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.BooleanField(default=False)),
                ('app', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='settings_list', to='applicationManager.Application')),
                ('setting', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='applicationManager.SettingDefinition')),
            ],
            options={
                'unique_together': {('app', 'setting')},
            },
        ),
    ]

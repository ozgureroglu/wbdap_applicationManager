# Generated by Django 2.2.4 on 2019-09-07 07:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('applicationManager', '0005_pagelayout_layout_icon_name'),
    ]

    operations = [
        migrations.RenameField(
            model_name='pagelayout',
            old_name='content',
            new_name='layout_template_code',
        ),
    ]

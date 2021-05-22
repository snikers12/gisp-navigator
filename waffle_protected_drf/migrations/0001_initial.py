# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-10-24 09:51
from __future__ import unicode_literals

from django.db import migrations, models
import waffle_protected_drf

# https://gist.github.com/destos/b808a601166fc8a74188

flag_name = waffle_protected_drf.FLAG_NAME


def update_waffle_forward(apps, schema_editor):
    Flag = apps.get_model('waffle', 'Flag')
    Flag.objects.update_or_create(
        name=flag_name,
        defaults={
            'superusers': True,
            'note': 'Enable Django Rest Framework Browsable API'
        }
    )


def update_waffle_backward(apps, schema_editor):
    Flag = apps.get_model('waffle', 'Flag')
    Flag.objects.get(name=flag_name).delete()


class Migration(migrations.Migration):
    dependencies = [
        ('waffle', '0002_auto_20161201_0958'),
    ]

    operations = [
        migrations.RunPython(update_waffle_forward, update_waffle_backward),
    ]

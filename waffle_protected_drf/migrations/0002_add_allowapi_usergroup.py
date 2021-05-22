# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-12-01 09:07
from __future__ import unicode_literals

from django.db import migrations
import waffle_protected_drf

group_name = waffle_protected_drf.GROUP_NAME
flag_name = waffle_protected_drf.FLAG_NAME


def forwards_func(apps, schema_editor):
    Group = apps.get_model("auth", 'Group')
    Flag = apps.get_model('waffle', 'Flag')

    group = Group.objects.create(name=group_name)
    group.save()

    flag = Flag.objects.get(name=flag_name)
    flag.groups.add(group)


def reverse_func(apps, schema_editor):
    Group = apps.get_model("auth", 'Group')
    Flag = apps.get_model('waffle', 'Flag')

    group = Group.objects.get(name=group_name)

    flag = Flag.objects.get(name=flag_name)
    flag.groups.remove(group)

    Group.objects.filter(name=group_name).delete()


class Migration(migrations.Migration):
    dependencies = [
        ('waffle_protected_drf', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(forwards_func, reverse_func),
    ]

# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-09-06 05:08
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='FederalSubject',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True, verbose_name='Название')),
                ('kladr_id', models.CharField(max_length=13, unique=True, verbose_name='Код КЛАДР')),
                ('email', models.EmailField(max_length=254, verbose_name='Почтовый адрес')),
            ],
            options={
                'verbose_name': 'Федеральный субъект',
                'verbose_name_plural': 'Федеральные субъекты',
            },
        ),
        migrations.CreateModel(
            name='FederalSubjectType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(max_length=30, unique=True, verbose_name='Полное название')),
                ('short_name', models.CharField(max_length=5, unique=True, verbose_name='Сокращенное название')),
                ('is_prefix', models.BooleanField(verbose_name='Название перед субъектом')),
            ],
            options={
                'verbose_name': 'Тип федерального субъекта',
                'verbose_name_plural': 'Типы федеральных субъектов',
            },
        ),
        migrations.AddField(
            model_name='federalsubject',
            name='federal_subject_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='regions.FederalSubjectType', verbose_name='Тип федерального субъекта'),
        ),
    ]

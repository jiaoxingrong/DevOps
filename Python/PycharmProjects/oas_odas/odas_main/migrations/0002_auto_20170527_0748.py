# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-05-27 07:48
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('odas_main', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='status',
            name='ansible_log',
            field=models.TextField(blank=True),
        ),
    ]

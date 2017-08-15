# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-05-26 09:15
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='IpAddress',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('project', models.CharField(max_length=50)),
                ('ip', models.CharField(max_length=20)),
                ('region', models.CharField(max_length=20)),
            ],
            options={
                'db_table': 'odas_ips',
            },
        ),
        migrations.CreateModel(
            name='ProjectInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('project', models.CharField(max_length=50)),
                ('git_repo', models.CharField(max_length=150)),
            ],
            options={
                'db_table': 'odas_info',
            },
        ),
        migrations.CreateModel(
            name='Status',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hashId', models.CharField(max_length=50)),
                ('project', models.CharField(max_length=50)),
                ('version', models.CharField(max_length=20)),
                ('status', models.CharField(max_length=50)),
                ('time', models.IntegerField()),
                ('ansible_log', models.TextField()),
            ],
            options={
                'db_table': 'odas_status',
            },
        ),
    ]

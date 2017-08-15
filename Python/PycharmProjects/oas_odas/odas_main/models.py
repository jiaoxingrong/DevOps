# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.


class ProjectInfo(models.Model):
    project = models.CharField(max_length=50)
    git_repo = models.CharField(max_length=150)

    class Meta:
        db_table = "odas_info"
        

class IpAddress(models.Model):
    # project = models.ForeignKey(ProjectInfo, ProjectInfo.project)
    project = models.CharField(max_length=50)
    ip = models.CharField(max_length=20)
    region = models.CharField(max_length=20)
    
    class Meta:
        db_table = "odas_ips"


class Status(models.Model):
    hashId = models.CharField(max_length=50)
    project = models.CharField(max_length=50)
    version = models.CharField(max_length=20)
    status = models.CharField(max_length=50)
    time = models.IntegerField()
    ansible_log = models.TextField(blank=True)
    
    class Meta:
        db_table = "odas_status"
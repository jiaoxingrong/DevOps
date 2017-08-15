# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from odas_main.models import *
# Register your models here.


class ProjectInfoAdmin(admin.ModelAdmin):
    list_display = ['project', 'git_repo']
    

class ProjectIpsAdmin(admin.ModelAdmin):
    list_display = ['project', 'ip', 'region']


class StatusAdmin(admin.ModelAdmin):
    list_display = ['hashId', 'project', 'version', 'status', 'time', 'ansible_log']


admin.site.register(ProjectInfo, ProjectInfoAdmin)
admin.site.register(IpAddress, ProjectIpsAdmin)
admin.site.register(Status, StatusAdmin)

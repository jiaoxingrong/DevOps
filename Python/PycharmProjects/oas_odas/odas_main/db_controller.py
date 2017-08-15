#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
__title__ = ''
__author__ = 'Jerome'
__mtime__ = '2017/5/26'

"""

from odas_main.models import *


class DBController():
    
    def select_zone_for_ip(self, project_name):
        sql_result = IpAddress.objects.filter(project=project_name)
        print project_name
        project_regions = [item.region for item in sql_result]
        return set(project_regions)
    
    def select_ip_for_ip(self, project_name, zone_name):
        sql_result = IpAddress.objects.filter(project=project_name, region=zone_name)
        project_ips = [item.ip for item in sql_result]
        return project_ips
    
    def insert_init_update_status(self, project_name, hash_key, code_version, create_time):
        new_state = Status(hashId=hash_key,
                           project=project_name,
                           version=code_version,
                           status='processing',
                           time=create_time)
        new_state.save()

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
__title__ = ''
__author__ = 'Jerome'
__mtime__ = '16/6/30'
# code is far away from bugs with the god animal protecting
    I love animals. They taste delicious.
             ┏┓   ┏┓
            ┏┛┻━━━┛┻┓
            ┃    ☃   ┃
            ┃ ┳┛  ┗┳┃
            ┃    ┻  ┃
            ┗━┓   ┏━┛
              ┃   ┗━━━┓
              ┃ 神兽保佑 ┣┓
              ┃ 永无BUG ! ┏┛
              ┗┓┓┏━┳┓┏┛
               ┃┫┫ ┃┫┫
               ┗┻┛ ┗┻┛
"""
import boto3
import time

class Route53():
    def __init__(self,service):
        self.client = boto3.client(
            service,
        )
        self.today = time.strftime('%Y-%m-%d',time.localtime(time.time()))
        self.export_filename = 'route53_export_' + self.today + '.csv'
        self.export_record_type = ['A','CNAME']

    def RequestAPI(self,zoneid):
        api_response = self.client.list_resource_record_sets(
            HostedZoneId=zoneid
        )
        return api_response

    def NextPageAPI(self,zoneid,StartName):
        api_response = self.client.list_resource_record_sets(
            HostedZoneId=zoneid,
            StartRecordName=StartName
        )
        return api_response

    def GetRecords(self):
        HostedZones = self.client.list_hosted_zones()
        HostedZonesId = [ hostedzone['Id'] for hostedzone in HostedZones['HostedZones'] ]

        # all_hosted_api_response = map(self.RequestAPI,HostedZonesId)
        domain_record_list = []
        for zoneid in HostedZonesId:
            page_res = self.RequestAPI(zoneid)
            domain_record_list.append(page_res['ResourceRecordSets'])
            if page_res['IsTruncated']:
                have_next_page = True
            while have_next_page:
                print have_next_page
                page_res = self.NextPageAPI(zoneid,page_res['NextRecordName'])
                if not page_res['IsTruncated']:
                    have_next_page = False
                domain_record_list.append(page_res['ResourceRecordSets'])

        f = file(self.export_filename,'wa')
        for record_set in domain_record_list:
            for record in record_set:
                if record.get('Type') in self.export_record_type and record.get('ResourceRecords'):
                    record_value = ''
                    for value in record['ResourceRecords']:
                        record_value += value['Value'] + ','
                    write_result = '%s,%s,%s\n' % (record['Name'],record['Type'],record_value)
                    f.write(write_result)

        f.close()

route53 = Route53('route53')
route53.GetRecords()

#!/usr/bin/env python
#coding: utf-8

import boto3
import time

#today = time.strftime('%Y-%m-%d',time.localtime(time.time()))
#
#client = boto3.client(
#    'route53',
aws_access_key_id = 'xx'
aws_secret_access_key = 'xx'
#
#)
#
#hostedzone_res = client.list_hosted_zones()
#HostedZoneIDs = [ hostedzone['Id'] for hostedzone in hostedzone_res['HostedZones']  ]
#
#record_sets = client.list_resource_record_sets(
#    HostedZoneId='/hostedzone/Z6PRES6OYXY7C',
#
#)
#
#record_sets_list = client.list_resource_record_sets(HostedZoneId)
#for i in record_sets['ResourceRecordSets']:
#print '%-20s%-6s%-20s' % (i['Name'],i['Type'],i['ResourceRecords'][0]['Value'])

class Route53():
    def __init__(self,key_id,secret_key,service):
        self.client = boto3.client(
            service,
            aws_access_key_id = key_id,
            aws_secret_access_key = secret_key
        )
        self.today = time.strftime('%Y-%m-%d',time.localtime(time.time()))
        self.export_filename = 'route53_export_' + self.today + '.csv'
        self.export_record_type = ['A','CNAME']

    def RequestAPI(self,arg):
        api_response = self.client.list_resource_record_sets(
            HostedZoneId = arg,
        )
        return api_response

    def GetRecords(self):
        HostedZones = self.client.list_hosted_zones()
        HostedZonesId = [ hostedzone['Id'] for hostedzone in HostedZones['HostedZones'] ]

        Domain_list = []

        all_hosted_api_response = map(self.RequestAPI,HostedZonesId)
       # for zone_id in HostedZonesId:
       #     api_res = self.client.list_resource_record_sets(
       #         HostedZoneId = zone_id
       #     )
       #     record_res = [ i for i in api_res['ResourceRecordSets'] ]

       #     for record in record_res:
       #         Domain_list.append((record['Name'],record['Type'],record['ResourceRecords'][0]['Value']))
       # return Domain_list
        f = file(self.export_filename,'wa')
        for hosted_record in all_hosted_api_response:
            record_res = [ i for i in hosted_record['ResourceRecordSets']  ]

            for record in record_res:
                #Domain_list.append((record['Name'],record['Type'],record['ResourceRecords'][0]['Value']))
                if record['Type'] in self.export_record_type:
                    write_result = '%s,%s,%s\n' % (record['Name'],record['Type'],record['ResourceRecords'][0]['Value'])
                    f.write(write_result)

        f.close()

route53 = Route53(aws_access_key_id,aws_secret_access_key,'route53')
route53.GetRecords()

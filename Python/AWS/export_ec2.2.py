#!/bin/env python
#coding: utf-8

import boto3
import time
import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


def GetEC2(region):
    #access_key = os.environ.get('AWS_ACCESS_KEY')
    #secret_key = os.environ.get('AWS_SECRET_KEY')
    today = time.strftime('%Y-%m-%d',time.localtime(time.time()))
    report_filename = 'export_ec2_'+today+'.csv'

    client = boto3.client(
        'ec2',
        region_name = region,
        #aws_access_key_id = access_key,
        #aws_secret_access_key = secret_key
    )

    api_response = client.describe_instances(
        Filters = [
            {
                'Name': 'instance-state-name',
                'Values' : [
                    'running'
                ]
            }
        ]
    )
    instances = [ i['Instances'][0] for i in api_response['Reservations'] ]
    f = file(report_filename,'a')
    f.seek(0,2)

    for instance in instances:
        for tag in instance['Tags']:
            if tag['Key'] == 'Name':
                instance_name = tag['Value']
        instance_ip = instance['PublicIpAddress']
        instance_type = instance['InstanceType']
        instance_launch_time = str(instance['LaunchTime'].strftime('%Y-%m-%d %H:%M:%S'))
        write_result = '%s,%s,%s,%s\n' % (instance_name,instance_type,instance_ip,instance_launch_time)
        f.write(write_result)
    f.close()

GetEC2('us-east-1')

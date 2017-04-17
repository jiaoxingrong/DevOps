#!/usr/bin/env python
#coding: utf-8
import boto3
import os
from datetime import datetime,timedelta

bucket = 'oas-elb-log'
before_days = timedelta(days=1)
date = datetime.now() - before_days
fixed_prefix = 'AWSLogs/027999362592/elasticloadbalancing/us-east-1/'
#date_prefix = time.strftime('%Y/%m/%d/',time.localtime(time.time()))
date_prefix = date.strftime('%Y/%m/%d/')
down_prefix = fixed_prefix + date_prefix

def down_file(bucket,prefix,save_path):
    client = boto3.client('s3')
    resource =boto3.resource('s3')
    paginator = client.get_paginator('list_objects')
    for result in paginator.paginate(Bucket=bucket,Delimiter='/',Prefix=prefix):
        if result.get('Contents') is not None:
            for file in result.get('Contents'):
                file_hour = file.get('LastModified').strftime('/%H/')
                file_storage_dir = os.path.dirname(save_path + os.sep + file.get('Key')) + file_hour
                if not os.path.exists(file_storage_dir):
                    os.makedirs(file_storage_dir)
                response = resource.meta.client.download_file(bucket, file.get('Key'), file_storage_dir + '/' + file.get('Key').split('/')[-1])

down_file(bucket,down_prefix,'/data/testdown')
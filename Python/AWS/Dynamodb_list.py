#!/bin/env python
#coding: utf-8
import boto3

region_contrast = {'ap-northeast-2': 'Asia Pacific (Seoul)', 'ap-south-1': 'Asia Pacific (Mumbai)', 'sa-east-1': 'South America (Sao Paulo)', 'eu-west-1': 'EU (Ireland)', 'eu-central-1': 'EU (Frankfurt)', 'ap-southeast-1': 'Asia Pacific (Singapore)', 'ap-southeast-2': 'Asia Pacific (Sydney)', 'us-west-1': 'US West (N. California)', 'ap-northeast-1': 'Asia Pacific (Tokyo)', 'us-west-2': 'US West (Oregon)', 'us-east-1': 'US East (N. Virginia)', 'us-east-2': 'US East (Ohio)'}

def GetTables(region,file_name):
    session = boto3.Session(
            region_name=region
        )
    client = session.client('dynamodb')
    response = client.list_tables()
    for table in response.get('TableNames'):
        print table,region_contrast.get(region)

Regions = ['eu-west-1','ap-southeast-1','ap-southeast-2','eu-central-1','ap-northeast-2','ap-northeast-1','us-east-1','sa-east-1','us-west-1','us-west-2']

for region in Regions:
    GetTables(region,'test.csv')

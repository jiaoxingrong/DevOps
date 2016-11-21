#!/bin/env python
#coding: utf-8

import boto3

def add_tag(region,ins_id):
        session = boto3.session.Session(
            region_name = region
        )
        ec2 = session.client('ec2')
        response = ec2.create_tags(
            Resources = ins_id,
            Tags=[
                {
                    'Key': 'Project',
                    'Value': 'google-pay'
                },
            ]
        )

inss = ['i-e453ad43', 'i-eb53ad4c', 'i-82f9c326', 'i-3594ae91', 'i-3694ae92', 'i-88584d2c', 'i-117a7bb5', 'i-127a7bb6', 'i-643830c0', 'i-663830c2', 'i-673830c3', 'i-783830dc', 'i-793830dd', 'i-84bfab20', 'i-85bfab21', 'i-47687ee3', 'i-87f1e023', 'i-419b8be5', 'i-74b2a1d0', 'i-75b2a1d1', 'i-7ab2a1de', 'i-f2b0a356', 'i-fed9c55a', 'i-ffd9c55b', 'i-48ded9c6', 'i-49ded9c7', 'i-514951f5', 'i-5e4951fa', 'i-aa322a0e', 'i-ab322a0f', 'i-98332b3c', 'i-a1e3f905', 'i-a2e3f906', 'i-75ac49d2', 'i-e0d23747', 'i-5b51b5fc', 'i-c0a04367', 'i-c1a04366', 'i-a8e8fe26', 'i-abe8fe25', 'i-82fced0c', 'i-5c6986fb', 'i-84799723', 'i-d05ab477', 'i-d75ab470', 'i-4d7099ea', 'i-a6739a01', 'i-28c72c8f', 'i-29c72c8e', 'i-2bc72c8c', 'i-d6c72c71', 'i-dc92677b', 'i-6b7f8acc', 'i-787f8adf', 'i-08b246af', 'i-0bb246ac', 'i-84817723', 'i-9a81773d', 'i-9b81773c', 'i-3ba3599c', 'i-3ca3599b', 'i-3da3599a', 'i-3ea35999', 'i-3fa35998']

# for ins in inss:
add_tag('ap-southeast-1',inss)

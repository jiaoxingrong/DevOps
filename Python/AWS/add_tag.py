#!/bin/env python
#coding: utf-8

import boto3

def add_tag(region,ins_id):
        session = boto3.session.Session(
            region_name = region
        )
        ec2 = session.client('ec2')

        try:
            response = ec2.create_tags(
                Resources = ins_id,
                Tags=[
                    {
                        'Key': 'Project',
                        'Value': 'google-pay'
                    },
                ]
            )
        except:
            print response
inss = ['i-b28130aa','i-9a91f582']
# for ins in inss:
add_tag('us-east-1',inss)

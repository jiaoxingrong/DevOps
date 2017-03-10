#!/bin/env python
#coding: utf-8
import boto3

session = boto3.Session(
        profile_name='platform',
        region_name='us-east-1'
    )

ec2 = session.client('ec2')

response = ec2.describe_instances()
print response
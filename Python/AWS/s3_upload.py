#!/bin/env python
#coding: utf-8
import boto3

session = boto3.Session(
    profile_name='mdata',
    region_name='us-west-2'
)
s3 = session.resource('s3')
s3.meta.client.upload_file('/home/ec2-user/passport_user.tar.gz', 'brotlab-mdata5-export', 'seven/passport_user.tar.gz')

#!/bin/env python
#coding: utf-8
import boto3

s3 = boto3.resource('s3')
s3.meta.client.upload_file('add_tag.py', 'oas-pay3-payment', 'mykey.txt')

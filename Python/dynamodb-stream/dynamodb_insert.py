#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
__title__ = ''
__author__ = 'Jerome'
__mtime__ = '2017/3/13'

"""

import boto3
import json

session = boto3.Session(
    profile_name='mdata',
    region_name='ap-northeast-1'
)

dynamodb = session.resource('dynamodb')
table = dynamodb.Table('stream_export_test')

f = file('/Users/Jerome/Downloads/insert_text.txt')
with table.batch_writer() as batch:
    
    for line in f:
        text = json.loads(line)
        for k, y in text.items():
            
            batch.put_item(
                Item={
                    'account_type': 'anonymous',
                    'username': 'user' + str(i),
                    'first_name': 'unknown',
                    'last_name': 'unknown'
                }
            )
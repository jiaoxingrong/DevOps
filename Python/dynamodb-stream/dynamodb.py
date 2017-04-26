#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
__title__ = ''
__author__ = 'Jerome'
__mtime__ = '2017/3/10'

"""

import boto3
session = boto3.Session(
    profile_name='beijing',
    region_name='cn-north-1'
)

stream = session.client('dynamodbstreams')
response = stream.describe_stream(
    StreamArn='arn:aws-cn:dynamodb:cn-north-1:341381255897:table/xingrong-stream-test/stream/2017-03-10T02:44:07.701'
)
# print response.get('StreamDescription').get('Shards')


shard_response = stream.get_shard_iterator(
    StreamArn='arn:aws-cn:dynamodb:cn-north-1:341381255897:table/xingrong-stream-test/stream/2017-03-10T02:44:07.701',
    # ShardId='shardId-00000001489113848684-ee81ebd5',
    ShardId='shardId-00000001489127491228-bcc998b3',
    ShardIteratorType='TRIM_HORIZON'
)

# print shard_response

record_res = stream.get_records(
    ShardIterator=shard_response['ShardIterator']
)

print record_res.get('Records')

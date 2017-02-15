#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
__title__ = ''
__author__ = 'Jerome'
__mtime__ = '2017/2/10'

"""
import boto3

response = client.create_table(
    AttributeDefinitions=[
        {
            'AttributeName': 'string',
            'AttributeType': 'S'|'N'|'B'
        },
    ],
    TableName='string',
    KeySchema=[
        {
            'AttributeName': 'string',
            'KeyType': 'HASH'|'RANGE'
        },
    ],
    GlobalSecondaryIndexes=[
        {
            'IndexName': 'string',
            'KeySchema': [
                {
                    'AttributeName': 'string',
                    'KeyType': 'HASH'|'RANGE'
                },
            ],
            'Projection': {
                'ProjectionType': 'ALL'|'KEYS_ONLY'|'INCLUDE',
                'NonKeyAttributes': [
                    'string',
                ]
            },
            'ProvisionedThroughput': {
                'ReadCapacityUnits': 123,
                'WriteCapacityUnits': 123
            }
        },
    ],
    ProvisionedThroughput={
        'ReadCapacityUnits': 123,
        'WriteCapacityUnits': 123
    },
    StreamSpecification={
        'StreamEnabled': True|False,
        'StreamViewType': 'NEW_IMAGE'|'OLD_IMAGE'|'NEW_AND_OLD_IMAGES'|'KEYS_ONLY'
    }
)
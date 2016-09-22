#!/usr/bin/env python
#coding: utf-8
import time
import boto3
client = boto3.client('cloudfront')

response = client.create_invalidation(
    DistributionId='E16S6B1FMKSF4N',
    InvalidationBatch={
        'Paths': {
            'Quantity': 1,
            'Items': [
                '/*',
            ]
        },
        'CallerReference': str(time.time())
    } 
)

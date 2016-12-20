#!/bin/env python
#coding: utf-8
import boto3

session = boto3.Session(
    profile_name='ses',
    region_name='us-east-1'
)

client = session.client('ses')
response = client.send_email(
    Source='support@cs.oasgames.com',
    Destination={
        'ToAddresses': [
            'jiaoxingrong@oasgames.com',
        ]
    },
    Message={
        'Subject': {
            'Data': 'Test mail',
            'Charset': 'utf-8'
        },
        'Body': {
            'Text': {
                'Data': 'This is an test mail',
                'Charset': 'utf-8'
            }
        }
    },
    ReplyToAddresses=[
        'support@cs.oasgames.com',
    ]
)

print response

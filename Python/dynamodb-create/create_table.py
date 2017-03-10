#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
__title__ = ''
__author__ = 'Jerome'
__mtime__ = '2017/2/10'

"""
import boto3


class DynamoDBTable:
    def __init__(self, profile, region):
        session = boto3.Session(
            profile_name=profile,
            region_name=region
        )
        self.dynamodb = session.client('dynamodb')

    def create_table(self, table_name, attr_def_list, key_schema, gsi_list=''):
        if gsi_list:
            response = self.dynamodb.create_table(
                AttributeDefinitions=attr_def_list,
                TableName=table_name,
                KeySchema=key_schema,
                GlobalSecondaryIndexes=gsi_list,
                ProvisionedThroughput={
                    'ReadCapacityUnits': 5,
                    'WriteCapacityUnits': 5
                },
                StreamSpecification={
                    'StreamEnabled': True,
                    'StreamViewType': 'NEW_AND_OLD_IMAGES'
                }
            )
        else:
            response = self.dynamodb.create_table(
                AttributeDefinitions=attr_def_list,
                TableName=table_name,
                KeySchema=key_schema,
                ProvisionedThroughput={
                    'ReadCapacityUnits': 5,
                    'WriteCapacityUnits': 5
                },
                StreamSpecification={
                    'StreamEnabled': True,
                    'StreamViewType': 'NEW_AND_OLD_IMAGES'
                }
            )
            
        return response
    
    def desc_arn(self, table_name):
        response = self.dynamodb.describe_table(
            TableName=table_name
        )
        table_arn = response.get('Table').get('TableArn')
        return table_arn


def main():
    TableName = 'dynamodb_create_test'
    
    AttributeDefinitions = [
        {
            'AttributeName': 'uid',
            'AttributeType': 'N'
        },
        {
            'AttributeName': 'user_name',
            'AttributeType': 'S'
        }
    ]
    KeySchema = [
            {
                'AttributeName': 'user_name',
                'KeyType': 'HASH'
            },
            {
                'AttributeName': 'uid',
                'KeyType': 'RANGE'
            }
    ]
    GlobalSecondaryIndexes = [
            {
                'IndexName': 'test_index1',
                'KeySchema': [
                    {
                        'AttributeName': 'orders_str',
                        'KeyType': 'HASH'
                    },
                    {
                        'AttributeName': 'orders_id',
                        'KeyType': 'RANGE'
                    }
                ],
                'Projection': {
                    'ProjectionType': 'KEYS_ONLY'
                },
                'ProvisionedThroughput': {
                    'ReadCapacityUnits': 5,
                    'WriteCapacityUnits': 5
                }
            }
    ]
    print create_table('mdata', 'ap-northeast-1', TableName, AttributeDefinitions, KeySchema)


if __name__ == '__main__':
    main()

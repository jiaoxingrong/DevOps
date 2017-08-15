#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
__title__ = ''
__author__ = 'Jerome'
__mtime__ = '2017/2/9'

"""

import boto3
import time


class DynamoDBCloudWatch:
    def __init__(self, profile, region):
        self.region = region
        session = boto3.Session(
            region_name=region,
            profile_name=profile
        )
        self.dynamodb = session.client('dynamodb')
        self.cloudwatch = session.client('cloudwatch')
        self.alarm_metrics = ['ReadThrottleEvents', 'WriteThrottleEvents']
        self.alarm_action = 'arn:aws:sns:' + region + ':027999362592:dynamodb'

    def get_all_dynamodb(self):
        paginator = self.dynamodb.get_paginator('list_tables')
        tables = []
        for page in paginator.paginate():
            tables.extend(page.get('TableNames'))

        return tables
    
    def get_table_all_index(self, table):
        response = self.dynamodb.describe_table(
            TableName=table
        )
        
        response = response.get('Table').get('GlobalSecondaryIndexes')
        if response:
            indexes = [i.get('IndexName') for i in response]
            return indexes
        
    def table_add_alarm(self, table):
        for metric in self.alarm_metrics:
            alarm_name = 'aws-dynamodb-' + table + '-High-' + metric
            self.cloudwatch.put_metric_alarm(
                AlarmName=alarm_name,
                ActionsEnabled=True,
                OKActions=[
                    self.alarm_action,
                ],
                AlarmActions=[
                    self.alarm_action,
                ],
                MetricName=metric,
                Namespace='AWS/DynamoDB',
                Statistic='Sum',
                # ExtendedStatistic='p50',
                Dimensions=[
                    {
                        'Name': 'TableName',
                        'Value': table
                    }
                ],
                Period=60,
                Unit='Count',
                EvaluationPeriods=5,
                Threshold=1,
                ComparisonOperator='GreaterThanOrEqualToThreshold'
            )
    
    def indexes_add_alarm(self, table, index):
        for metric in self.alarm_metrics:
            alarm_name = 'aws-dynamodb-' + table + '-' + index + '-High-' + metric
            self.cloudwatch.put_metric_alarm(
                AlarmName=alarm_name,
                ActionsEnabled=True,
                OKActions=[
                    self.alarm_action,
                ],
                AlarmActions=[
                    self.alarm_action,
                ],
                MetricName=metric,
                Namespace='AWS/DynamoDB',
                Statistic='Sum',
                # ExtendedStatistic='p50',
                Dimensions=[
                    {
                        'Name': 'TableName',
                        'Value': table
                    },
                    {
                        'Name': 'GlobalSecondaryIndexName',
                        'Value': index
                    }
                ],
                Period=60,
                Unit='Count',
                EvaluationPeriods=5,
                Threshold=1,
                ComparisonOperator='GreaterThanOrEqualToThreshold'
            )
    
    def run(self, table):
        self.table_add_alarm(table)
        table_indexes = self.get_table_all_index(table)
        if table_indexes:
            for index in table_indexes:
                self.indexes_add_alarm(table, index)
            
            
def main():
    regions = ['ap-northeast-1', 'eu-central-1', 'us-east-1']
    for region in regions:
        dynamodb = DynamoDBCloudWatch('platform', region)
        tables = dynamodb.get_all_dynamodb()
        for dynamodb_table in tables:
            dynamodb.table_add_alarm(dynamodb_table)
            print 'region: %s, table: %s, alarm add success!' % (region, dynamodb_table)
            
            dynamodb_table_indexes = dynamodb.get_table_all_index(dynamodb_table)
            if dynamodb_table_indexes:
                for index in dynamodb_table_indexes:
                    dynamodb.indexes_add_alarm(dynamodb_table, index)
                    print 'region: %s, table: %s, index: %s, alarm add success!' % (region, dynamodb_table, index)


def update_dynamodb(profile, region):
    dynamodb = DynamoDBCloudWatch(profile, region)
    tables = dynamodb.get_all_dynamodb()
    for table in tables:
        gsi_update_data_list = []
        dynamodb_table_indexes = dynamodb.get_table_all_index(table)
        if dynamodb_table_indexes:
            for index in dynamodb_table_indexes:
                gsi_update_data = {
                                'Update': {
                                    'IndexName': index,
                                    'ProvisionedThroughput': {
                                        'ReadCapacityUnits': 1,
                                        'WriteCapacityUnits': 1
                                    }
                                }
                            }
                gsi_update_data_list.append(gsi_update_data)
            try:
                response = dynamodb.dynamodb.update_table(
                    TableName=table,
                    ProvisionedThroughput={
                        'ReadCapacityUnits': 1,
                        'WriteCapacityUnits': 1
                    },
                    GlobalSecondaryIndexUpdates=gsi_update_data_list,
                )
                
                print response
                time.sleep(5)
                
            except Exception, e:
                print Exception, e
                
if __name__ == '__main__':
    # main()
    update_dynamodb('beijing', 'cn-north-1')

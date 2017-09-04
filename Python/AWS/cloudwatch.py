#!/bin/env python
import boto3

session = boto3.Session(region_name='us-east-1')
cloudwatch = session.client('cloudwatch')

paginator = cloudwatch.get_paginator('describe_alarms')

operation_parameters = {'StateValue': 'ALARM'}

for page in paginator.paginate(**operation_parameters):
    alarms = page['MetricAlarms']
    for alarm in alarms:
        # print alarm.get('AlarmName'),alarm.get('StateUpdatedTimestamp')
        print alarm

# response = cloudwatch.describe_alarms(
#     StateValue='ALARM',
# )

# print response['MetricAlarms'][0]['AlarmName']
# print response['MetricAlarms'][0]['Namespace']
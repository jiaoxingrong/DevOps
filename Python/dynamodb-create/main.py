#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
from flask import Flask, render_template, request
from create_table import DynamoDBTable
from create_cloudwatch import DynamoDBCloudWatch
from aws_policy import DynamoDBPolicy

app = Flask(__name__)

aws_profile = 'platform'

token_config = {
    'SxrgZToidObM': {'odp3': {'policy': 'arn:aws:iam::027999362592:policy/oas-odp3-dynamodb-web-create'}},
    'PKemDuhlFJnr': {'pay3': {'policy': 'arn:aws:iam::027999362592:policy/oas-pay3-dynamodb-web-create'}}
}


def process_data(table_details):
    input_token = table_details.get('token')
    input_project = table_details.get('project')
    
    if not input_token and not input_project:
        return '项目或Token不能为空！'
    
    if input_token not in token_config:
        return '不存在的Token！'
        
    if input_project not in token_config.get(input_token):
        return 'Token与项目不匹配！'
        
    region = table_details.get('region')
    table_info = table_details.get('table')
    table_name = table_info.get('name')
    table_primary_key = table_info.get('PrimaryKey').get('name')
    table_primary_key_type = table_info.get('PrimaryKey').get('type')[0]
    table_key_schema = [
        {
            'AttributeName': table_primary_key,
            'KeyType': 'HASH'
        }
    ]
    attribute_definitions = [{
        'AttributeName': table_primary_key,
        'AttributeType': table_primary_key_type
    }]
    if table_info.get('SortKey'):
        table_sort_key = table_info.get('SortKey').get('name')
        table_sort_key_type = table_info.get('SortKey').get('type')[0]
        table_sort_key_attr = {
            'AttributeName': table_sort_key,
            'AttributeType': table_sort_key_type
        }
        attribute_definitions.append(table_sort_key_attr)
        table_sort_key_schema = {
            'AttributeName': table_sort_key,
            'KeyType': 'RANGE'
        }
        table_key_schema.append(table_sort_key_schema)

    global_secondary_indexes = []
    
    if table_info.get('gsi'):
        for gsi in table_info.get('gsi'):
            index_name = gsi
            gsi_info = table_info.get('gsi').get(gsi)
            projection = gsi_info.get('ProAttr')
            gsi_primary_key = gsi_info.get('PrimaryKey').get('name')
            gsi_primary_key_type = gsi_info.get('PrimaryKey').get('type')[0]
            gsi_data = {
                'IndexName': index_name,
                'KeySchema': [
                    {
                        'AttributeName': gsi_primary_key,
                        'KeyType': 'HASH'
                    }
                ],
                'Projection': {
                    'ProjectionType': projection
                },
                'ProvisionedThroughput': {
                    'ReadCapacityUnits': 5,
                    'WriteCapacityUnits': 5
                }
            }
            gsi_attribute_def = {
                'AttributeName': gsi_primary_key,
                'AttributeType': gsi_primary_key_type
            }
            attribute_definitions.append(gsi_attribute_def)
            if gsi_info.get('SortKey'):
                gsi_sort_key = gsi_info.get('SortKey').get('name')
                gsi_sort_key_type = gsi_info.get('SortKey').get('type')[0]
                gsi_sort_key_def = {
                    'AttributeName': gsi_sort_key,
                    'AttributeType': gsi_sort_key_type
                }
                attribute_definitions.append(gsi_sort_key_def)
                gsi_sort_key_schema = {
                    'AttributeName': gsi_sort_key,
                    'KeyType': 'RANGE'
                }
                gsi_data['KeySchema'].append(gsi_sort_key_schema)
            global_secondary_indexes.append(gsi_data)
    try:
        table = DynamoDBTable(aws_profile, region)
        table.create_table(table_name, attribute_definitions, table_key_schema, global_secondary_indexes)
    except Exception, e:
        result = '创建表失败，错误为：' + str(Exception) + ": " + str(e)
        return result
    
    try:
        cloudwatch = DynamoDBCloudWatch(aws_profile, region)
        cloudwatch.run(table_name)
    except Exception, e:
        result = '为表创建CloudWatch报警失败，错误为：' + str(Exception) + ": " + str(e)
        return result
     
    try:
        table_arn = table.desc_arn(table_name)
        resource_list = [table_arn, table_arn + '/*']
        project_policy_arn = token_config.get(input_token).get(input_project).get('policy')
        policy = DynamoDBPolicy(aws_profile, project_policy_arn)
        policy.run(resource_list)
    except Exception, e:
        result = '为表分配权限失败，错误为：' + str(Exception) + ": " + str(e)
        return result
        
    with file('create.log', 'a') as f:
        f.seek(0, 2)
        now = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        log = '%s | %s | %s | %s | success\n' % (now, input_project, table_name, region)
        f.write(log)
    
    return '已成功创建表，已成功为表添加CloudWatch报警, 已成功分配权限。'


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api', methods=['POST'])
def api():
    post_data = request.form.get('data')
    table_details = eval(post_data)
    print table_details
    result = process_data(table_details)
    return result

if __name__ == '__main__':
    app.run(debug=True)

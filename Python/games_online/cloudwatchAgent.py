#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
__title__ = ''
__author__ = 'Jerome'
__mtime__ = '2017/7/21'
"""

# from jinja2 import Environment, FileSystemLoader
import boto3


def cloudwatch_logs(region, group, stream, keyword, name):
    session = boto3.Session(
        profile_name='platform',
        region_name=region
    )
    logs = session.client('logs')
    logs.create_log_group(
        logGroupName=group,
        tags={
            'Name': group
        }
    )
    logs.create_log_stream(
        logGroupName=group,
        logStreamName=stream
    )
    logs.client.put_metric_filter(
        logGroupName=group,
        filterName='cloudwatch-logs-filter-' + name,
        filterPattern=keyword,
        metricTransformations=[
            {
                'metricName': 'cloudwatch-logs-' + name + '-encounter-error',
                'metricNamespace': 'LogMetrics',
                'metricValue': '1',
            },
        ]
)

agent_config = {
    '52.23.108.196': [
        {
            'name': 'oas-pay2-web2',
            'region': 'us-east-1',
            'file': '/data/log/alerts_log/*/',
            'keyword': '/data/a.log',
            'group': 'oas-uqp',
            'stream': 'oas-uqp-web1',
            # 'line_format': '',
            'date_format': '[%Y-%m-%d %H:%M:%S]',
        },
        {
            'name': 'oas-uqp',
            'region': 'ap-northeast-1',
            'file': '/data/b.log',
            'group': 'oas-uqp',
            'stream': 'oas-uqp-web1',
            # 'line_format': '',
            'date_format': '[%Y-%m-%d %H:%M:%S]',
        },
    ]
}

# env = Environment(loader=FileSystemLoader('templates'))
# tpl = env.get_template('shell.tpl')

for key in agent_config:
    ipAddress = key
    configs = agent_config.get(key)
    rotateFiles = []
    context = """# !/bin/bash -

yum install awslogs - y

cat > /etc/awslogs/awscli.conf <<EOF
[plugins]
cwlogs = cwlogs
[default]
region = %s
EOF

cat > /etc/awslogs/awslogs.conf <<EOF
[general]
state_file = /var/lib/awslogs/agent-state
EOF

cat >> /etc/awslogs/awslogs.conf <<EOF
""" % (configs[0].get('region'))
    
    for config in configs:
        keyword = config.get('keyword')
        name = config.get('name')
        region = config.get('region')
        filePath = config.get('file')
        rotateFiles.append(filePath)
        logStream = config.get('stream')
        logGroup = config.get('group')
        lineFormat = config.get('line_format')
        dateFormat = config.get('date_format')
        generateFile = name + '_agent_install.sh'
        if dateFormat:
            context += """
[%s]
datetime_format = %s
time_zone = UTC
file = %s
buffer_duration = 5000
log_stream_name = %s
initial_position = end_of_file
multi_line_start_pattern = {datetime_format}
log_group_name = %s
""" % (name, dateFormat, filePath, logStream, logGroup)
        else:
            context += """[%s]
time_zone = UTC
file = %s
buffer_duration = 5000
log_stream_name = %s
initial_position = end_of_file
multi_line_start_pattern = %s
log_group_name = %s
""" % (name, filePath, logStream, lineFormat, logGroup)
    
    context += """EOF
    
cat > /etc/logrotate.d/project_alert_log <<EOF
"""
    
    for rotateFile in rotateFiles:
        context += """
%s {
    missingok
    notifempty
    size 100M
    create
    delaycompress
    compress
    rotate 4
}
""" % rotateFile
    
    context += 'EOF'
    with open(generateFile, 'wb') as f:
        f.write(context.encode('utf-8'))

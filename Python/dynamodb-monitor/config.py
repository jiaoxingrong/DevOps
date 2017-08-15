#!/bin/env python
#coding: utf-8

aws_profile                = 'default'
aws_region                 = 'ap-northeast-1'
#各种配置的路径，需带最后位置的'/'
dynamic_dynamodb_conf_path = '/etc/dynamic-dynamodb/'
log_path                   = '/data/log/dynamodb-monitor/'
pidfile_path               = '/var/run/dynamodb-monitor/'
#运行程序的绝对路径，不带最后的'/''
app                        = '/usr/local/bin/dynamic-dynamodb'
exclude_tables             = []
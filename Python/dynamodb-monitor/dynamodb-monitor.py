#!/bin/env python
# coding: utf-8

import os
import commands
import boto3
from jinja2 import Environment, FileSystemLoader
from config import *

aws_access_key = os.getenv('aws_access_key')
aws_access_secret = os.getenv('aws_access_secret')


class dynamodbtables():
    """docstring for dynamodbtables"""
    
    def __init__(self, profile, region):
        self.profile = profile
        self.region = region
    
    def getTables(self):
        session = boto3.Session(
            profile_name=self.profile,
            region_name=self.region
        )
        dynamodb = session.client('dynamodb')
        response = dynamodb.list_tables()
        return response.get('TableNames')


def checkTablesApp(conf_dir, tables_list):
    if not os.path.isdir(conf_dir):
        os.makedirs(conf_dir)
    
    table_conf_list = os.listdir(conf_dir)
    table_name_from_conf = [i.split('.')[0] for i in table_conf_list]
    new_tables = set(tables_list) - set(table_name_from_conf)
    del_tables = set(table_name_from_conf) - set(tables_list)
    if new_tables:
        for table in new_tables:
            addTableConf(table)
            startApp(table)
    if del_tables:
        for table in del_tables:
            delTableConf(table)
            stoptApp(table)
    
    new_table_conf_list = os.listdir(conf_dir)
    new_table_name_from_conf = [i.split('.')[0] for i in new_table_conf_list]
    for table in new_table_name_from_conf:
        checkAppStatus(table)


def addTableConf(table):
    env = Environment(loader=FileSystemLoader('templates'))
    tpl = env.get_template('dynamic-dynamodb.conf.tpl')
    table_conf_file = dynamic_dynamodb_conf_path + table + '.conf'
    log_file = log_path + table + '.log'
    table_conf = tpl.render(
        aws_access_key=aws_access_key,
        aws_access_secret=aws_access_secret,
        aws_region=aws_region,
        log_file=log_file,
        table=table
    )
    with open(table_conf_file, 'wb') as conf_file:
        conf_file.write(table_conf.encode('utf-8'))


def delTableConf(table):
    table_conf_file = dynamic_dynamodb_conf_path + table + '.conf'
    cmd_res = commands.getstatusoutput('rm -f ' + table_conf_file)
    if cmd_res[0] != 0:
        print cmd_res[1]


def startApp(table):
    if not os.path.isdir(log_path):
        os.makedirs(log_path)
    table_pidfile_path = pidfile_path + table
    if not os.path.isdir(table_pidfile_path):
        os.makedirs(table_pidfile_path)
    start_cmd = app + ' -c ' + dynamic_dynamodb_conf_path + table + '.conf' + ' --pid-file-dir ' + table_pidfile_path + ' --daemon start'
    cmd_res = commands.getstatusoutput(start_cmd)
    if cmd_res[0] != 0:
        print cmd_res[1]


def stoptApp(table):
    stop_cmd = app + ' -c ' + dynamic_dynamodb_conf_path + table + '.conf' + ' --pid-file-dir ' + pidfile_path + table + ' --daemon stop'
    cmd_res = commands.getstatusoutput(stop_cmd)
    if cmd_res[0] != 0:
        print cmd_res[1]


def checkAppStatus(table):
    check_cmd = app + ' -c ' + dynamic_dynamodb_conf_path + table + '.conf' + ' --pid-file-dir ' + pidfile_path + table + ' --daemon start'
    cmd_res = commands.getstatusoutput(check_cmd)
    if cmd_res[0] == 0:
        print 'The process of checking table %s is crash !!' % (table)


def main():
    dynamodb = dynamodbtables(aws_profile, aws_region)
    all_tables_list = dynamodb.getTables()
    need_check_tables = set(all_tables_list) - set(exclude_tables)
    checkTablesApp(dynamic_dynamodb_conf_path, need_check_tables)


if __name__ == '__main__':
    main()

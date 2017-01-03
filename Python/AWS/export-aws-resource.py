#!/bin/env python
#coding: utf-8

import boto3
import time
import sys
import datetime
import calendar
import csv
from collections import namedtuple
from sqlalchemy import create_engine, Table, Column, MetaData, select, INTEGER, VARCHAR, Float, and_

reload(sys)
sys.setdefaultencoding('GBK')

region_contrast = {'ap-northeast-2': 'Asia Pacific (Seoul)', 'ap-south-1': 'Asia Pacific (Mumbai)', 'sa-east-1': 'South America (Sao Paulo)', 'eu-west-1': 'EU (Ireland)', 'eu-central-1': 'EU (Frankfurt)', 'ap-southeast-1': 'Asia Pacific (Singapore)', 'ap-southeast-2': 'Asia Pacific (Sydney)', 'us-west-1': 'US West (N. California)', 'ap-northeast-1': 'Asia Pacific (Tokyo)', 'us-west-2': 'US West (Oregon)', 'us-east-1': 'US East (N. Virginia)', 'us-east-2': 'US East (Ohio)'}

def cal_run_hours(cal_date,compare_date=datetime.datetime.utcnow().strftime('%Y%m')):
    compare_date = str(compare_date)
    if int(compare_date[-2:]) == 1:
        compare_date_year = int(compare_date[:4]) - 1
        compare_date_month = 12
    else:
        compare_date_year = int(compare_date[:4])
        compare_date_month = int(compare_date[-2:]) - 1

    compare_date_month_hours = calendar.monthrange(compare_date_year,compare_date_month)[1] * 24
    compare_date_begin_ts = calendar.timegm(datetime.datetime(compare_date_year,compare_date_month,1).timetuple())

    if compare_date_month == '12':
        compare_date_end_ts = calendar.timegm(datetime.datetime(compare_date_year+1,1,1).timetuple())
    else:
        compare_date_end_ts = calendar.timegm(datetime.datetime(compare_date_year,compare_date_month+1,1).timetuple())

    # print compare_date_begin_time,compare_date_end_time,compare_date_month_hours
    cal_date_ts = calendar.timegm(cal_date.timetuple())

    run_hours = 0

    if compare_date_begin_ts < cal_date_ts < compare_date_end_ts:
        run_hours = (compare_date_end_ts - cal_date_ts) / 3600

    if cal_date_ts < compare_date_begin_ts:
        run_hours = compare_date_month_hours

    return run_hours

def get_ec2_price(region,instance_type,platform):
    engine = create_engine('mysql+mysqlconnector://root:123456@localhost:3306/aws_price',encoding='utf-8')
    metadata = MetaData()
    ec2_price = Table('ec2',metadata,
        Column('id',INTEGER,primary_key=True),
        Column('service',VARCHAR(50)),
        Column('region',VARCHAR(50)),
        Column('instance_type',VARCHAR(50)),
        Column('platform',VARCHAR(50)),
        Column('price',Float))
    conn = engine.connect()

    w_sql = and_(
            ec2_price.c.region == region,
            ec2_price.c.instance_type == instance_type,
            ec2_price.c.platform == platform
        )
    s = select([ec2_price.c.price]).where(w_sql)
    r = conn.execute(s)
    res = r.fetchall()
    if res:
        return res[0][0]
def GetEC2(profile,region,report_filename,compare_date=0):
    region_name = region_contrast.get(region)
    f = file(report_filename,'a')
    f.seek(0,2)

    session = boto3.Session(
        profile_name=profile,
        #aws_access_key_id=access_key,
        #aws_secret_access_key=secret_key,
        region_name=region
    )

    client = session.client('ec2')

    api_response = client.describe_vpcs()
    vpc_ids = [ vpc_id['VpcId'] for vpc_id in api_response['Vpcs'] ]

    # f.write('\n'+region+'\n')

    client = session.resource('ec2')
    for vpc_id in vpc_ids:
        VPC = client.Vpc(vpc_id)
        instances = VPC.instances.all()
        if not instances:
            return

        for instance in instances:
            if instance.state['Name'] == 'running':
                for tag in instance.tags:
                    if tag.get('Key') == 'Name':
                        instance_name = tag['Value']

                    if tag.get('Key') == 'Project':
                        instance_project = tag.get('Value')
                try:
                    instance_project
                except Exception, e:
                    instance_project = 'Null'

                try:
                    instance_volume_size = 0
                    # # instance_pri_ip =  instance.private_ip_address
                    # instance_ip = instance.classic_address.public_ip
                    instance_type = instance.instance_type

                    if compare_date:
                        instance_run_hours = cal_run_hours(instance.launch_time,compare_date)
                    else:
                        instance_run_hours = cal_run_hours(instance.launch_time)

                    instance_id = instance.instance_id

                    for v in  instance.volumes.all():
                        instance_volume_size += v.size

                    if instance.platform:
                        inst_platform = 'Windows'
                    else:
                        inst_platform = 'Linux'
                    single_price = get_ec2_price(region,instance_type,inst_platform)
                    month_price = instance_run_hours * single_price
                    write_result = '%s,%s,%s,%s,%d,%.2f,%d,%s\n' % ('EC2',
                        instance_project, instance_name, instance_type, instance_run_hours, month_price, instance_volume_size,region_name)
                    f.write(write_result)
                except Exception,e:
                    print Exception, ":", e, instance_name
    f.close()
def GetEC2v2(profile,region,report_filename,compare_date=0):
    result_dict = {}
    region_name = region_contrast.get(region)
    f = file(report_filename,'a')
    f.seek(0,2)
    session = boto3.Session(
        profile_name=profile,
        region_name=region
    )
    client = session.client('ec2')
    api_response = client.describe_vpcs()
    vpc_ids = [ vpc_id['VpcId'] for vpc_id in api_response['Vpcs'] ]
    client = session.resource('ec2')
    for vpc_id in vpc_ids:
        VPC = client.Vpc(vpc_id)
        instances = VPC.instances.all()
        if not instances:
            return
        for instance in instances:
            if instance.state['Name'] == 'running':
                for tag in instance.tags:
                    if tag.get('Key') == 'Name':
                        instance_name = tag['Value']

                    if tag.get('Key') == 'Project':
                        instance_project = tag.get('Value')
                try:
                    instance_project
                except Exception, e:
                    instance_project = instance_name
                try:
                    instance_volume_size = 0
                    instance_type = instance.instance_type
                    if compare_date:
                        instance_run_hours = cal_run_hours(instance.launch_time,compare_date)
                    else:
                        instance_run_hours = cal_run_hours(instance.launch_time)

                    instance_id = instance.instance_id

                    for v in  instance.volumes.all():
                        instance_volume_size += v.size

                    if instance.platform:
                        inst_platform = 'Windows'
                    else:
                        inst_platform = 'Linux'
                    single_price = get_ec2_price(region,instance_type,inst_platform)
                    month_price = instance_run_hours * single_price

                    if result_dict.get(instance_project):
                        if result_dict.get(instance_project).get('ec2').get(instance_type):
                            result_dict[instance_project]['ec2'][instance_type]['hours'] += instance_run_hours
                            result_dict[instance_project]['ec2'][instance_type]['prices'] += month_price
                            result_dict[instance_project]['ec2'][instance_type]['num'] += 1
                            result_dict[instance_project]['ebs'] += instance_volume_size
                        else:
                            result_dict[instance_project]['ec2'][instance_type] = {'hours': 0, 'prices': 0 ,'num': 0}
                            result_dict[instance_project]['ec2'][instance_type]['hours'] += instance_run_hours
                            result_dict[instance_project]['ec2'][instance_type]['prices'] += month_price
                            result_dict[instance_project]['ec2'][instance_type]['num'] += 1
                            result_dict[instance_project]['ebs'] += instance_volume_size
                    else:
                        result_dict[instance_project] = {'ec2':{},'ebs':0}
                        result_dict[instance_project]['ec2'][instance_type] = {'hours': 0, 'prices': 0 ,'num': 0}
                        result_dict[instance_project]['ec2'][instance_type]['hours'] += instance_run_hours
                        result_dict[instance_project]['ec2'][instance_type]['prices'] += month_price
                        result_dict[instance_project]['ec2'][instance_type]['num'] += 1
                        result_dict[instance_project]['ebs'] += instance_volume_size

                except Exception,e:
                    print Exception, ":", e, instance_name

    for project in result_dict:
        for type in result_dict.get(project).get('ec2'):
            ins_type_info = result_dict.get(project).get('ec2').get(type)
            write_result = '%s,%s,%s,%d,%d,%.2f,%s\n' % (project,'EC2', type, ins_type_info.get('num'),ins_type_info.get('hours'), ins_type_info.get('prices'), region_name)
            f.write(write_result)
        wrt_ebs_result = '%s,%s,,%d,,,%s\n' % (project,'EBS',result_dict.get(project).get('ebs'),region_name)
        f.write(wrt_ebs_result)
    f.close()

def GetELB(profile,region,report_filename):
    result_dict = {}
    region_name = region_contrast.get(region)
    f = file(report_filename,'a')
    f.seek(0,2)

    session = boto3.Session(
        profile_name=profile,
        region_name=region
    )
    client = session.client('elb')
    api_response = client.get_paginator('describe_load_balancers')
    paginator = api_response.paginate()
    elb_names = []
    for page in paginator:
        items = page.get('LoadBalancerDescriptions')
        for elb in items:
            elb_name = elb.get('LoadBalancerName')
            get_elb_tag = client.describe_tags(
                    LoadBalancerNames=[elb_name]
                )
            for tag in get_elb_tag.get('TagDescriptions')[0].get('Tags'):
                if tag.get('Key') == 'Project':
                    elb_project = tag.get('Value')
            try:
                elb_project
            except Exception, e:
                elb_project = 'Null'

            if result_dict.get(elb_project):
                result_dict[elb_project] += 1
            else:
                result_dict[elb_project] = 1

    for elb in result_dict:
        write_result = '%s,%s,,%d,,,%s\n' % (elb, 'ELB', result_dict.get(elb), region_name)
        f.write(write_result)
    f.close()

def get_rds_price(region,instance_type,db_engine,deploymentOption):
    engine = create_engine('mysql+mysqlconnector://root:123456@localhost:3306/aws_price',encoding='utf-8')
    metadata = MetaData()
    rds_price = Table('rds',metadata,
        Column('id',INTEGER,primary_key=True),
        Column('service',VARCHAR(50)),
        Column('region',VARCHAR(50)),
        Column('instance_type',VARCHAR(50)),
        Column('engine',VARCHAR(50)),
        Column('deploymentOption',VARCHAR(50)),
        Column('price',Float))
    conn = engine.connect()

    w_sql = and_(
            rds_price.c.region == region,
            rds_price.c.instance_type == instance_type,
            rds_price.c.engine == db_engine,
            rds_price.c.deploymentOption == deploymentOption
        )
    s = select([rds_price.c.price]).where(w_sql)
    r = conn.execute(s)
    res = r.fetchall()
    if res:
        return res[0][0]
def GetRDS(profile,account,region,report_filename,compare_date=0):
    result_dict = {}
    region_name = region_contrast.get(region)
    f = file(report_filename,'a')
    f.seek(0,2)

    session = boto3.Session(
        profile_name=profile,
        region_name=region
    )
    client = session.client('rds')
    api_response = client.describe_db_instances()
    DBIns = api_response.get('DBInstances')
    if not DBIns:
        return

    for db in DBIns:
        db_name = db.get('DBInstanceIdentifier')
        db_storage = db.get('AllocatedStorage')
        db_engine = db.get('Engine')
        db_ins_type = db.get('DBInstanceClass')
        db_arn = 'arn:aws:rds:' + region + ':' + account + ':db' + ':' + db_name

        db_tags = client.list_tags_for_resource(ResourceName=db_arn)
        for tag in db_tags.get('TagList'):
            if tag.get('Key') == 'Project':
                db_project = tag.get('Value')

        try:
            db_project
        except Exception, e:
            db_project = 'Null'

        if db.get('MultiAZ'):
            db_IF_MultiAZ = 'Multi-AZ'
        else:
            db_IF_MultiAZ = 'Single-AZ'

        if compare_date:
            db_run_hours = cal_run_hours(db.get('InstanceCreateTime'),compare_date)
        else:
            db_run_hours = cal_run_hours(db.get('InstanceCreateTime'))

        single_price = get_rds_price(region, db_ins_type, db_engine, db_IF_MultiAZ)
        if not single_price:
            print region, db_ins_type, db_engine, db_IF_MultiAZ
        db_month_price = db_run_hours * single_price

        if result_dict.get(db_project):
            if result_dict.get(db_project).get('rds').get(db_ins_type):
                result_dict[db_project]['rds'][db_ins_type]['hours'] += db_run_hours
                result_dict[db_project]['rds'][db_ins_type]['prices'] += db_month_price
                result_dict[db_project]['rds'][db_ins_type]['num'] += 1
                result_dict[db_project]['rds-storage'] += db_storage
            else:
                result_dict[db_project]['rds'][db_ins_type] = {'hours': 0, 'prices': 0 ,'num': 0}
                result_dict[db_project]['rds'][db_ins_type]['hours'] += db_run_hours
                result_dict[db_project]['rds'][db_ins_type]['prices'] += db_month_price
                result_dict[db_project]['rds'][db_ins_type]['num'] += 1
                result_dict[db_project]['rds-storage'] += db_storage
        else:
            result_dict[db_project] = {'rds':{},'rds-storage':0}
            result_dict[db_project]['rds'][db_ins_type] = {'hours': 0, 'prices': 0 ,'num': 0}
            result_dict[db_project]['rds'][db_ins_type]['hours'] += db_run_hours
            result_dict[db_project]['rds'][db_ins_type]['prices'] += db_month_price
            result_dict[db_project]['rds'][db_ins_type]['num'] += 1
            result_dict[db_project]['rds-storage'] += db_storage

    for project in result_dict:
        for type in result_dict.get(project).get('rds'):
            db_type_info = result_dict.get(project).get('rds').get(type)
            write_result = '%s,%s,%s,%d,%d,%.2f,%s\n' % (project,'RDS', type, db_type_info.get('num'),db_type_info.get('hours'), db_type_info.get('prices'), region_name)
            f.write(write_result)
        wrt_ebs_result = '%s,%s,,%d,,,%s\n' % (project,'rds-storage',result_dict.get(project).get('rds-storage'),region_name)
        f.write(wrt_ebs_result)
    f.close()


def get_redshift_price(region,instance_type):
    engine = create_engine('mysql+mysqlconnector://root:123456@localhost:3306/aws_price',encoding='utf-8')
    metadata = MetaData()
    ec2_price = Table('redshift',metadata,
        Column('id',INTEGER,primary_key=True),
        Column('service',VARCHAR(50)),
        Column('region',VARCHAR(50)),
        Column('instance_type',VARCHAR(50)),
        Column('price',Float))
    conn = engine.connect()

    w_sql = and_(
            ec2_price.c.region == region,
            ec2_price.c.instance_type == instance_type,
        )
    s = select([ec2_price.c.price]).where(w_sql)
    r = conn.execute(s)
    res = r.fetchall()
    if res:
        return res[0][0]
def GetRedshift(profile, account, region, report_filename, compare_date=0):
    region_name = region_contrast.get(region)
    f = file(report_filename,'a')
    f.seek(0,2)

    session = boto3.Session(
        profile_name=profile,
        region_name=region
    )
    client = session.client('redshift')
    api_response = client.describe_clusters()

    Clusters = api_response.get('Clusters')
    if not Clusters:
        return

    for db in Clusters:
        db_name = db.get('ClusterIdentifier')
        db_node_num = db.get('NumberOfNodes')
        db_ins_type = db.get('NodeType')
        db_arn = 'arn:aws:redshift:' + region + ':' + account + ':cluster:' + db_name
        db_tags = client.describe_tags(
                ResourceName=db_arn,
                TagKeys=['Project']
            )

        for tag in db_tags.get('TaggedResources'):
            if tag.get('Tag').get('Key') == 'Project':
                db_project = tag.get('Tag').get('Value')
        try:
            db_project
        except Exception, e:
            db_project = db_name

        if compare_date:
            db_run_hours = cal_run_hours(db.get('ClusterCreateTime'),compare_date)
        else:
            db_run_hours = cal_run_hours(db.get('ClusterCreateTime'))

        single_price = get_redshift_price(region, db_ins_type)
        db_month_price = db_run_hours * single_price * db_node_num
        write_result = '%s,%s,%s,%d,%d,%.2f,%s\n' % (db_project, 'Redshift', db_ins_type, db_node_num, db_run_hours, db_month_price, region_name)
        f.write(write_result)
    f.close()


def get_elasticache_price(region,instance_type):
    engine = create_engine('mysql+mysqlconnector://root:123456@localhost:3306/aws_price',encoding='utf-8')
    metadata = MetaData()
    elasticache_price = Table('elasticache',metadata,
        Column('id',INTEGER,primary_key=True),
        Column('service',VARCHAR(50)),
        Column('region',VARCHAR(50)),
        Column('instance_type',VARCHAR(50)),
        Column('price',Float))
    conn = engine.connect()

    w_sql = and_(
            elasticache_price.c.region == region,
            elasticache_price.c.instance_type == instance_type,
        )
    s = select([elasticache_price.c.price]).where(w_sql)
    r = conn.execute(s)
    res = r.fetchall()
    if res:
        return res[0][0]
def GetElasticache(profile,account,region,report_filename,compare_date=0):
    region_name = region_contrast.get(region)
    f = file(report_filename,'a')
    f.seek(0,2)

    session = boto3.Session(
        profile_name=profile,
        region_name=region
    )
    client = session.client('elasticache')
    api_response = client.describe_cache_clusters()

    Clusters = api_response.get('CacheClusters')
    if not Clusters:
        return

    for db in Clusters:
        db_name = db.get('CacheClusterId')
        db_ins_type = db.get('CacheNodeType')

        db_arn = 'arn:aws:elasticache:' + region + ':' + account + ':cluster:' + db_name
        db_tags = client.list_tags_for_resource(ResourceName=db_arn)
        for tag in db_tags.get('TagList'):
            if tag.get('Key') == 'Project':
                db_project = tag.get('Value')

        try:
            db_project
        except Exception, e:
            db_project = db_name

        if compare_date:
            db_run_hours = cal_run_hours(db.get('CacheClusterCreateTime'),compare_date)
        else:
            db_run_hours = cal_run_hours(db.get('CacheClusterCreateTime'))

        single_price = get_elasticache_price(region, db_ins_type)
        db_month_price = db_run_hours * single_price
        write_result = '%s,%s,%s,,%d,%.2f,%s\n' % (db_project, 'Elasticache', db_ins_type, db_run_hours, db_month_price, region_name)
        f.write(write_result)
    f.close()

def final_statistical(resourceFile,resultingFile):
    final_dict = {}
    # = {Project:{'ec2':{'c4.large':{'number':  'hours':  ,'prices'  ,},'m4.large': }},'ebs':{'num': ,'prices': ,}, 'elb': {} ,}
    date = time.strftime('%Y-%m',time.localtime(time.time()))
    final_file_name = 'AWS-Bill-' + date + '.csv'
    final_f = open(resultingFile,'a')
    source_f = open(resourceFile)
    f_csv = csv.reader(source_f)
    headers = next(f_csv)
    Row = namedtuple('Row',headers)

    for r in f_csv:
        row = Row(*r)

        if final_dict.get(row.Project):
            if final_dict.get(row.Project).get(row.Service):
                if row.type:
                    if final_dict.get(row.Project).get(row.Service).get(row.type):
                        final_dict[row.Project][row.Service][row.type]['number'] += int(row.number)
                        final_dict[row.Project][row.Service][row.type]['hours']  += int(row.hours)
                        final_dict[row.Project][row.Service][row.type]['prices'] += float(row.prices)
                    else:
                            final_dict[row.Project][row.Service][row.type] = {'number': 0, 'hours': 0, 'prices': 0}
                            final_dict[row.Project][row.Service][row.type]['number'] += int(row.number)
                            final_dict[row.Project][row.Service][row.type]['hours']  += int(row.hours)
                            final_dict[row.Project][row.Service][row.type]['prices'] += float(row.prices)
                else:
                    final_dict[row.Project][row.Service]['number'] += int(row.number)
                    final_dict[row.Project][row.Service]['prices'] += float(row.prices)
            else:
                if row.type:
                    final_dict[row.Project][row.Service] = {}
                    final_dict[row.Project][row.Service][row.type] = {'number': 0, 'hours': 0, 'prices': 0}
                    final_dict[row.Project][row.Service][row.type]['number'] += int(row.number)
                    final_dict[row.Project][row.Service][row.type]['hours']  += int(row.hours)
                    final_dict[row.Project][row.Service][row.type]['prices'] += float(row.prices)
                else:
                    final_dict[row.Project][row.Service] = {'number': 0, 'prices': 0}
                    final_dict[row.Project][row.Service]['number'] += int(row.number)
                    final_dict[row.Project][row.Service]['prices'] += float(row.prices)
        else:
            if row.type:
                final_dict[row.Project] = {}
                final_dict[row.Project][row.Service] = {}
                final_dict[row.Project][row.Service][row.type] = {'number': 0, 'hours': 0, 'prices': 0}
                final_dict[row.Project][row.Service][row.type]['number'] += int(row.number)
                final_dict[row.Project][row.Service][row.type]['hours']  += int(row.hours)
                final_dict[row.Project][row.Service][row.type]['prices'] += float(row.prices)
            else:
                final_dict[row.Project] = {}
                final_dict[row.Project][row.Service] = {'number': 0, 'prices': 0}
                final_dict[row.Project][row.Service]['number'] += int(row.number)
                final_dict[row.Project][row.Service]['prices'] += float(row.prices)

    for project in final_dict:
        for service in final_dict.get(project):
            for type in final_dict.get(project).get(service):
                try:
                    hours = final_dict.get(project).get(service).get(type).get('hours')
                    number = final_dict.get(project).get(service).get(type).get('number')
                    prices = final_dict.get(project).get(service).get(type).get('prices')
                    wrt_res = '%s,%s,%s,%d,%d,%.2f\n' % (project,service,type,number,hours,prices)
                except Exception, e:
                    wrt_res = '%s,%s,,%d,,%.2f\n' % (project,service,number,prices)

                final_f.write(wrt_res)
    final_f.close()

def main(account):
    Regions = ['eu-west-1','ap-southeast-1','ap-southeast-2','eu-central-1','ap-northeast-2','ap-northeast-1','us-east-1','sa-east-1','us-west-1','us-west-2']

    today = time.strftime('%Y-%m-%d',time.localtime(time.time()))

    export_filename = 'export-aws-'+today+'.csv'

    with file(export_filename,'w') as f:
        f.write('Project,Service,type,number,hours,Prices,region\n')

    account_id = {'platform': '027999362592', 'mdata': '315771499375'}

    for region in Regions:
        # GetEC2(account, region, ec2_filename)
        GetEC2v2(account, region, export_filename)
        GetELB(account, region, export_filename)
        GetRDS(account, account_id.get(account), region,export_filename)
        GetRedshift(account, account_id.get(account), region,export_filename)
        GetElasticache(account, account_id.get(account), region,export_filename)

    final_statistical(export_filename, 'aws-bill-resulting.' + today + '.csv')

if __name__ == '__main__':
    main('platform')

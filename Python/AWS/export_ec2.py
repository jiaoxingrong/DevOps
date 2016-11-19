#!/bin/env python
#coding: utf-8

import boto3
import time
import sys
import datetime
import calendar
from sqlalchemy import create_engine, Table, Column, MetaData, select, INTEGER, VARCHAR, Float, and_

reload(sys)
sys.setdefaultencoding('GBK')

def cal_run_hours(cal_date,compare_date=datetime.datetime.utcnow().strftime('%Y%m')):
    compare_date = str(compare_date)
    compare_date_year = int(compare_date[:4])
    compare_date_month = int(compare_date[-2:])
    compare_date_month_hours = calendar.monthrange(compare_date_year,compare_date_month)[1] * 24
    compare_date_begin_ts = calendar.timegm(datetime.datetime(compare_date_year,compare_date_month,1).timetuple())

    if compare_date[-2:] == '12':
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
    engine = create_engine('mysql://root:123456@localhost:3006/aws_price',encoding='utf-8')
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
def GetEC2(region,report_filename,compare_date=0):
    #access_key = os.environ.get('AWS_ACCESS_KEY')
    #secret_key = os.environ.get('AWS_SECRET_KEY')

    f = file(report_filename,'a')
    f.seek(0,2)

    session = boto3.session.Session(
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
                    if tag['Key'] == 'Name':
                        instance_name = tag['Value']
                try:
                    instance_volume_size = 0
                    instance_pri_ip =  instance.private_ip_address
                    instance_ip = instance.classic_address.public_ip
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
                    write_result = '%s,%s,%s,%d,%.2f,%d,%s\n' % ('EC2',instance_name, instance_type, instance_run_hours, month_price, instance_volume_size,region)
                    f.write(write_result)
                except:
                    print instance
    f.close()


def get_rds_price(region,instance_type,db_engine,deploymentOption):
    engine = create_engine('mysql://root:123456@localhost:3006/aws_price',encoding='utf-8')
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
def GetRDS(region,report_filename,compare_date=0):

    f = file(report_filename,'a')
    f.seek(0,2)

    session = boto3.session.Session(
        #aws_access_key_id=access_key,
        #aws_secret_access_key=secret_key,
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
        write_result = '%s,%s,%s,%d,%.2f,%d,%s\n' % ('RDS',db_name, db_ins_type, db_run_hours, db_month_price, db_storage, region)
        f.write(write_result)
    f.close()


def get_redshift_price(region,instance_type):
    engine = create_engine('mysql://root:123456@localhost:3006/aws_price',encoding='utf-8')
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
def GetRedshift(region,report_filename,compare_date=0):
    f = file(report_filename,'a')
    f.seek(0,2)

    session = boto3.session.Session(
        #aws_access_key_id=access_key,
        #aws_secret_access_key=secret_key,
        region_name=region
    )
    client = session.client('redshift')
    api_response = client.describe_clusters()

    Clusters = api_response.get('Clusters')
    if not Clusters:
        return

    for db in Clusters:
        db_name = db.get('ClusterIdentifier')
        db_ins_type = db.get('NodeType')

        if compare_date:
            db_run_hours = cal_run_hours(db.get('ClusterCreateTime'),compare_date)
        else:
            db_run_hours = cal_run_hours(db.get('ClusterCreateTime'))

        single_price = get_redshift_price(region, db_ins_type)
        db_month_price = db_run_hours * single_price
        write_result = '%s,%s,%s,%d,%.2f,%s\n' % ('Redshift',db_name, db_ins_type, db_run_hours, db_month_price, region)
        f.write(write_result)
    f.close()


def get_elasticache_price(region,instance_type):
    engine = create_engine('mysql://root:123456@localhost:3006/aws_price',encoding='utf-8')
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
def GetElasticache(region,report_filename,compare_date=0):
    f = file(report_filename,'a')
    f.seek(0,2)

    session = boto3.session.Session(
        #aws_access_key_id=access_key,
        #aws_secret_access_key=secret_key,
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

        if compare_date:
            db_run_hours = cal_run_hours(db.get('CacheClusterCreateTime'),compare_date)
        else:
            db_run_hours = cal_run_hours(db.get('CacheClusterCreateTime'))

        single_price = get_elasticache_price(region, db_ins_type)
        db_month_price = db_run_hours * single_price
        write_result = '%s,%s,%s,%d,%.2f,%s\n' % ('Elasticache',db_name, db_ins_type, db_run_hours, db_month_price, region)
        f.write(write_result)
    f.close()

def main():
    Regions = ['eu-west-1','ap-southeast-1','ap-southeast-2','eu-central-1','ap-northeast-2','ap-northeast-1','us-east-1','sa-east-1','us-west-1','us-west-2']
    today = time.strftime('%Y-%m-%d',time.localtime(time.time()))

    report_filename = '/Users/Jerome/Desktop/export_aws_'+today+'.csv'

    for region in Regions:
        GetEC2(region,report_filename)
        # GetRDS(region,report_filename)
        # GetRedshift(region,report_filename)
        # GetElasticache(region,report_filename)

if __name__ == '__main__':
    main()


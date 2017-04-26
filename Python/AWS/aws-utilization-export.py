#!/bin/env python
#coding: utf-8

import boto3
import datetime
import time
import sys
import calendar

reload(sys)
sys.setdefaultencoding('GBK')

CloudWatch_Config = {
        'EC2': {'Dimensions': ['InstanceId'], 'Metrics': ['CPUUtilization']},
        'RDS': {'Dimensions': ['DBInstanceIdentifier'], 'Metrics': ['CPUUtilization', 'FreeableMemory']},
        'Redshift': {'Dimensions':['ClusterIdentifier'], 'Metrics': ['CPUUtilization']},
        'ElastiCache': {'Dimensions': ['CacheClusterId','CacheNodeId'], 'Metrics': ['CPUUtilization','FreeableMemory']}
    }

CacheTotalMem = {'cache.r3.large':  14495514624, 'cache.t2.medium':  3457448673.28, 'cache.t2.small':  1664299827.2, 'cache.t2.micro':  595926712.32}
RDSTotalMem = {'cache.r3.large':  14495514624, 'cache.t2.medium':  3457448673.28, 'cache.t2.small':  1664299827.2, 'cache.t2.micro':  595926712.32}

region_contrast = {
    'ap-northeast-2': 'Asia Pacific (Seoul)', 'ap-south-1': 'Asia Pacific (Mumbai)', 'sa-east-1': 'South America (Sao Paulo)', 'eu-west-1': 'EU (Ireland)', 'eu-central-1': 'EU (Frankfurt)', 'ap-southeast-1': 'Asia Pacific (Singapore)', 'ap-southeast-2': 'Asia Pacific (Sydney)', 'us-west-1': 'US West (N. California)', 'ap-northeast-1': 'Asia Pacific (Tokyo)', 'us-west-2': 'US West (Oregon)', 'us-east-1': 'US East (N. Virginia)', 'us-east-2': 'US East (Ohio)'
    }

# def GetCloudWatchData(profile, region, Namespace, Dimensions, MetricName, Date=datetime.datetime.utcnow().strftime('%Y%m')):
def GetCloudWatchData(profile, region, Namespace, Dimensions, MetricName, Date='201703'):
    year = int(Date[:4])
    month = int(Date[-2:])

    session = boto3.Session(profile_name=profile, region_name=region)
    client = session.client('cloudwatch')

    start_time = datetime.datetime(year,month,1)
    end_time = datetime.datetime(year,month,calendar.monthrange(year,month)[1])
    start_time = start_time.isoformat()
    end_time = end_time.isoformat()

    response = client.get_metric_statistics(
        Namespace = Namespace,
        MetricName = MetricName,
        Dimensions = Dimensions,
        # Dimensions=[
            # {
            #     'Name':'ClusterIdentifier',
            #     'Value': 'oas-pay'
            # },
            # {
            #     'Name':'NodeID',
            #     'Value': 'Compute-0'
            # }
        # ],
        StartTime=start_time,
        EndTime=end_time,
        Period=3600,
        Statistics=[
            'Average'
        ]
    )
    DataPoints = [ i.get('Average') for i in response.get('Datapoints') ]
    return DataPoints

def GetEC2(profile, acconut, region, report_filename, compare_date=0):
    region_name = region_contrast.get(region)
    f = file(report_filename,'a')
    f.seek(0,2)
    CloudWatch_Metrics = CloudWatch_Config.get('EC2').get('Metrics')
    # file_header = '%s,%s,%s,' % ('Services','Name','Type')
    # for metric in CloudWatch_Metrics:
    #     file_header += metric + ','
    # file_header += 'Region\n'
    # f.write(file_header)

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
            break
        for instance in instances:
            if instance.state['Name'] == 'running':
                for tag in instance.tags:
                    if tag.get('Key') == 'Name':
                        instance_name = tag['Value']
                    if tag.get('Key') == 'Project':
                        instance_project = tag.get('Value')
                try:
                    instance_type = instance.instance_type
                    instance_id = instance.instance_id
                    Dimensions = [{'Name': 'InstanceId', 'Value': instance_id}]
                    file_body = '%s,%s,%s,%s' %  ('EC2', instance_project, instance_name, instance_type)

                    for metric in CloudWatch_Metrics:
                        if compare_date:
                            DataPoints = GetCloudWatchData(profile, region, 'AWS/EC2', Dimensions, metric, compare_date)
                        else:
                            DataPoints = GetCloudWatchData(profile, region, 'AWS/EC2', Dimensions, metric)

                        DataPoints_AVG = '%.2f,' % (sum(DataPoints)/len(DataPoints))
                        DataPoints_MAX = '%.2f,' % max(DataPoints)
                        file_body += str(DataPoints_AVG) + DataPoints_MAX
                    file_body += region_name + '\n'
                    f.write(file_body)
                except Exception,e:
                    print instance_name
                    print Exception,":", e
    f.close()

def GetRDS(profile, acconut, region, report_filename, compare_date=0):
    region_name = region_contrast.get(region)
    f = file(report_filename,'a')
    f.seek(0,2)
    CloudWatch_Metrics = CloudWatch_Config.get('RDS').get('Metrics')
    file_header = '%s,%s,%s,' % ('Services','Name','Type')
    for metric in CloudWatch_Metrics:
        file_header += metric + ','
    file_header += 'Region\n'
    f.write(file_header)

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
        db_arn = 'arn:aws:rds:' + region + ':' + account + ':db' + ':' + db_name
        db_tags = client.list_tags_for_resource(ResourceName=db_arn)
        db_name = db.get('DBInstanceIdentifier')
        db_ins_type = db.get('DBInstanceClass')
        for tag in db_tags.get('TagList'):
            if tag.get('Key') == 'Project':
                db_project = tag.get('Value')
        try:
            db_project
        except Exception as e:
            db_project = db_name
        Dimensions = [{'Name': 'DBInstanceIdentifier', 'Value': db_name}]
        file_body = '%s,%s,%s,%s' %  ('RDS', db_project, db_name, db_ins_type)

        for metric in CloudWatch_Metrics:
            if compare_date:
                DataPoints = GetCloudWatchData(profile, region, 'AWS/RDS', Dimensions, metric, compare_date)
            else:
                DataPoints = GetCloudWatchData(profile, region, 'AWS/RDS', Dimensions, metric)
            try:
                DataPoints_AVG = '%.2f,' % (sum(DataPoints)/len(DataPoints))
                DataPoints_MIN = '%.2f,' % (min(DataPoints))
                DataPoints_MAX = '%.2f,' % (max(DataPoints))
                file_body += str(DataPoints_AVG) + DataPoints_MIN + DataPoints_MAX
            except Exception, e:
                print db_name
                print Exception,":", e
        file_body += region_name + '\n'
        f.write(file_body)
    f.close()

def GetRedshift(profile, acconut, region, report_filename, compare_date=0):
    region_name = region_contrast.get(region)
    f = file(report_filename,'a')
    f.seek(0,2)
    CloudWatch_Metrics = CloudWatch_Config.get('Redshift').get('Metrics')
    file_header = '%s,%s,%s,%s,' % ('Services','Name','Type','NodeNum')
    for metric in CloudWatch_Metrics:
        file_header += metric + ','
    file_header += 'Region\n'
    f.write(file_header)

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

        Dimensions = [{'Name': 'ClusterIdentifier', 'Value': db_name}]
        file_body = '%s,%s,%s,%s,%d,' %  ('Redshift', db_project, db_name, db_ins_type, db_node_num)

        for metric in CloudWatch_Metrics:
            if compare_date:
                DataPoints = GetCloudWatchData(profile, region, 'AWS/Redshift', Dimensions, metric, compare_date)
            else:
                DataPoints = GetCloudWatchData(profile, region, 'AWS/Redshift', Dimensions, metric)
            try:
                DataPoints_AVG = '%.2f,' % (sum(DataPoints)/len(DataPoints))
                DataPoints_MAX = '%.2f,' % max(DataPoints)
                file_body += str(DataPoints_AVG) + DataPoints_MAX
            except Exception, e:
                pass
        file_body += region_name + '\n'
        f.write(file_body)
    f.close()

def GetElastiCache(profile, acconut, region, report_filename, compare_date=0):
    region_name = region_contrast.get(region)
    f = file(report_filename,'a')
    f.seek(0,2)
    CloudWatch_Metrics = CloudWatch_Config.get('ElastiCache').get('Metrics')
    file_header = '%s,%s,%s,' % ('Services','Name','Type')
    for metric in CloudWatch_Metrics:
        file_header += metric + ','
    file_header += 'Region\n'
    f.write(file_header)

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

        Dimensions = [{'Name': 'CacheClusterId', 'Value': db_name}]
        file_body = '%s,%s,%s,%s' %  ('ElastiCache', db_project, db_name, db_ins_type)

        for metric in CloudWatch_Metrics:
            if compare_date:
                DataPoints = GetCloudWatchData(profile, region, 'AWS/ElastiCache', Dimensions, metric, compare_date)
            else:
                DataPoints = GetCloudWatchData(profile, region, 'AWS/ElastiCache', Dimensions, metric)
            try:
                DataPoints_AVG = '%.2f,' % (sum(DataPoints)/len(DataPoints))
                DataPoints_MIN = '%.2f,' % (min(DataPoints))
                DataPoints_MAX = '%.2f,' % (max(DataPoints))
                file_body += str(DataPoints_AVG) + DataPoints_MIN + DataPoints_MAX
            except Exception, e:
                print Exception,":", e
        file_body += region_name + '\n'
        f.write(file_body)
    f.close()

if __name__ == '__main__':
    # Dimensions = [{'Name': 'CacheClusterId', 'Value': 'console-oasgames'}]
    # print GetCloudWatchData('platform', 'us-east-1', 'AWS/ElastiCache', Dimensions, 'CPUUtilization')
    Regions = ['eu-west-1','ap-southeast-1','ap-southeast-2','eu-central-1','ap-northeast-2','ap-northeast-1','us-east-1','sa-east-1','us-west-1','us-west-2']
    today = time.strftime('%Y-%m-%d',time.localtime(time.time()))
    report_filename = 'aws-utilization-'
    account_ids = {'platform': '027999362592', 'mdata': '315771499375', 'datacenter': '352826524974'}
    profile = 'platform'
    account_id = account_ids.get('account')
    for region in Regions:
        GetEC2(profile, account_id, region, report_filename + '-EC2-' + today + '.csv')
        GetRDS(profile, account_id, region, report_filename + '-RDS-' + today + '.csv')
        GetRedshift(profile, account_id, region, report_filename + '-Redshift-' + today + '.csv')
        GetElastiCache(profile, account_id, region, report_filename + '-ElastiCache-' + today + '.csv')

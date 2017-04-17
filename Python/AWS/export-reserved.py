#!/bin/env python
#coding: utf-8
import boto3
import time
import datetime


def ec2reserve(session, report_file, region_name, profile):
    ec2 = session.client('ec2')
    response = ec2.describe_reserved_instances()
    if not response.get('ReservedInstances'):
        return
    with file(report_file, 'a') as f:
        f.seek(0,2)
        for resvere_ins in response.get('ReservedInstances'):
            if resvere_ins.get('State') == 'active':
                wrt_result = '%s,%s,%s,%s,%s,%s\n' % (resvere_ins.get('ProductDescription'), resvere_ins.get('InstanceType'), resvere_ins.get('InstanceCount'), resvere_ins.get('End'), region_name, profile)
                f.write(wrt_result)


def rdsreserve(session, report_file, region_name, profile):
    rds = session.client('rds')
    response = rds.describe_reserved_db_instances()
    if not response.get('ReservedDBInstances'):
        return

    with file(report_file, 'a') as f:
        f.seek(0,2)
        for resvere_ins in response.get('ReservedDBInstances'):
            if resvere_ins.get('State') == 'active':
                duration = resvere_ins.get('Duration')
                time_delta = datetime.timedelta(seconds=duration)
                expired_time = resvere_ins.get('StartTime') + time_delta
                wrt_result = '%s,%s,%s,%s,%s,%s,%s\n' % (resvere_ins.get('ProductDescription'), resvere_ins.get('DBInstanceClass'), resvere_ins.get('DBInstanceCount'), expired_time, region_name, profile, resvere_ins.get('MultiAZ'))
                f.write(wrt_result)


def redshiftreserve(session, report_file, region_name, profile):
    redshift = session.client('redshift')
    response = redshift.describe_reserved_nodes()
    print response
    if not response.get('ReservedDBInstances'):
        return

    with file(report_file, 'a') as f:
        f.seek(0,2)
        for resvere_ins in response.get('ReservedDBInstances'):
            if resvere_ins.get('State') == 'active':
                duration = resvere_ins.get('Duration')
                time_delta = datetime.timedelta(seconds=duration)
                expired_time = resvere_ins.get('StartTime') + time_delta
                wrt_result = '%s,%s,%s,%s,%s,%s\n' % ('Redshift', resvere_ins.get('NodeType'), resvere_ins.get('NodeCount'), expired_time, region_name, profile)
                f.write(wrt_result)


def cachereserve(session, report_file, region_name, profile):
    elasticache = session.client('elasticache')
    response = elasticache.describe_reserved_cache_nodes()
    if not response.get('ReservedCacheNodes'):
            return

    with file(report_file, 'a') as f:
        f.seek(0,2)
        for resvere_ins in response.get('ReservedCacheNodes'):
            if resvere_ins.get('State') == 'active':
                duration = resvere_ins.get('Duration')
                time_delta = datetime.timedelta(seconds=duration)
                expired_time = resvere_ins.get('StartTime') + time_delta
                wrt_result = '%s,%s,%s,%s,%s,%s\n' % (resvere_ins.get('ProductDescription'), resvere_ins.get('CacheNodeType'), resvere_ins.get('CacheNodeCount'), expired_time, region_name, profile)
                f.write(wrt_result)


def main(profile):
    # regions = ['eu-west-1','ap-southeast-1','ap-southeast-2','eu-central-1','ap-northeast-2','ap-northeast-1','us-east-1','sa-east-1','us-west-1','us-west-2']
    regions = ['us-east-1']
    region_contrast = {
    'ap-northeast-2': 'Asia Pacific (Seoul)', 'ap-south-1': 'Asia Pacific (Mumbai)', 'sa-east-1': 'South America (Sao Paulo)', 'eu-west-1': 'EU (Ireland)', 'eu-central-1': 'EU (Frankfurt)', 'ap-southeast-1': 'Asia Pacific (Singapore)', 'ap-southeast-2': 'Asia Pacific (Sydney)', 'us-west-1': 'US West (N. California)', 'ap-northeast-1': 'Asia Pacific (Tokyo)', 'us-west-2': 'US West (Oregon)', 'us-east-1': 'US East (N. Virginia)', 'us-east-2': 'US East (Ohio)'
    }
    today = time.strftime('%Y-%m-%d', time.localtime(time.time()))
    report_file = 'aws-reserve-instance-' + today + '.csv'
    for region in regions:
        session = boto3.Session(
                profile_name=profile,
                region_name=region
            )
        # ec2reserve(session, report_file, region_contrast.get(region), profile)
        # rdsreserve(session, report_file, region_contrast.get(region), profile)
        redshiftreserve(session, report_file, region_contrast.get(region), profile)
        # cachereserve(session, report_file, region_contrast.get(region), profile)

if __name__ == '__main__':
    profiles = ['mdata', 'platform', 'datacenter']
    for profile in profiles:
        main(profile)

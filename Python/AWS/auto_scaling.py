#!/bin/env python
#coding: utf-8

import boto3
import datetime
import time

today = time.strftime('%Y-%m-%d',time.localtime(time.time()))

log_file = 'aws_auto_scaling' + today + '.log'

def get_cloudwatch(instance_list):
    client = boto3.client('cloudwatch')
    end_time = datetime.datetime.utcnow()
    start_time = end_time - datetime.timedelta(minutes=2)
    end_time = end_time.isoformat()
    start_time = start_time.isoformat()

    api_result = []
    f = file(log_file,'a')
    for ec2_id in instance_list:
        response = client.get_metric_statistics(
            Namespace='AWS/EC2',
            MetricName='NetworkIn',
            Dimensions=[
                {
                    'Name':'InstanceId',
                    'Value':ec2_id
                }
            ],
            StartTime=start_time,
            EndTime=end_time,
            Period=60,
            Statistics=[
                'Average'
            ]
        )
        write_res = str(response) + '\n'
        f.write(write_res)
        data_point = response['Datapoints'][0]['Average']
        api_result.append(data_point)
    f.close()
    return api_result

def start_ec2(InstanceId):
    client = boto3.client('ec2')
    response = client.start_instances(
        InstanceIds=[
            InstanceId,
        ]
    )
    with file(log_file,'a') as f:
        write_res = str(response) + '\n'
        f.write(write_res)

    if 'pending' == response['StartingInstances'][0]['CurrentState']['Name']:
        return True
    else:
        return False


def get_ec2_status(InstanceId):
    client = boto3.client('ec2')
    response = client.describe_instance_status(
        InstanceIds=[
            InstanceId,
        ],
    )

    with file(log_file,'a') as f:
        write_res = str(response) + '\n'
        f.write(write_res)

    sys_status = response['InstanceStatuses'][0]['SystemStatus']['Status']
    instance_status = response['InstanceStatuses'][0]['InstanceState']['Name']

    if 'ok' == sys_status and 'running' == instance_status:
        return True
    else:
        return False

def attach_elb(InstanceId,elb_name):
    client = boto3.client('elb')
    response = client.register_instances_with_load_balancer(
        LoadBalancerName=elb_name,
        Instances=[
            {
                'InstanceId':InstanceId
            }
        ]
    )
    with file(log_file,'a') as f:
        write_res = str(response) + '\n'
        f.write(write_res)

def main():
    monitor_ec2 = ['i-36b03ab1','i-8cd7c217','i-3656b4aa']
    backup_ec2 = ['i-34ed66a4']
    alarm_state = False
    alarm_count = 0
    while True:
        print alarm_state
        print alarm_count
        if not alarm_state:
            monitor_values = get_cloudwatch(monitor_ec2)
            for i in monitor_values:
                if i >= 786432000:
                    alarm_count += 1
                    break
            if alarm_count >= 5:
                start_ec2(backup_ec2[0])
                time.sleep(300)
                while True:
                    if get_ec2_status(backup_ec2[0]):
                        alarm_state = True
                        attach_elb(backup_ec2[0],'ODP-http-ELB')
                        with file(log_file,'a') as f:
                            f.write('Start EC2 to elb : ok;\n')
                        break
        time.sleep(60)

if __name__ == '__main__':
    main()

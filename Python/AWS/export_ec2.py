#!/bin/env python
#coding: utf-8

import boto3
import time
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


def GetEC2(region):
    #access_key = os.environ.get('AWS_ACCESS_KEY')
    #secret_key = os.environ.get('AWS_SECRET_KEY')
    today = time.strftime('%Y-%m-%d',time.localtime(time.time()))
    report_filename = 'export_ec2_'+today+'.csv'

    session = boto3.session.Session(
        #aws_access_key_id=access_key,
        #aws_secret_access_key=secret_key,
        region_name=region
    )

    client = session.client('ec2')

    api_response = client.describe_vpcs()
    vpc_ids = [ vpc_id['VpcId'] for vpc_id in api_response['Vpcs'] ]

    f = file(report_filename,'a')
    f.seek(0,2)
    #f.write('\n'+region+'\n')

    client = session.resource('ec2')
    for vpc_id in vpc_ids:
        VPC = client.Vpc(vpc_id)
        instances = VPC.instances.all()
        for instance in instances:
            if instance.state['Name'] == 'running':
                for tag in instance.tags:
                    if tag['Key'] == 'Name':
                        instance_name = tag['Value']
                try:
                    instance_pri_ip =  instance.private_ip_address
                    instance_ip = instance.classic_address.public_ip
                    instance_type = instance.instance_type
                    instance_launch_time = instance.launch_time
                    instance_id = instance.instance_id
                except:
                    print instance
                # write_result = '%s,%s,%s,%s,%s,%s\n' % (instance_name, instance_type, instance_ip, instance_pri_ip, instance_launch_time, instance_id)
                write_result = '%s,%s,%s,%s\n' % (instance_name, instance_type, instance_launch_time,region)
                f.write(write_result)
    f.close()

def main():
    Regions = ['eu-west-1','ap-southeast-1','ap-southeast-2','eu-central-1','ap-northeast-2','ap-northeast-1','us-east-1','sa-east-1','us-west-1','us-west-2']
    for region in Regions:
        GetEC2(region)

if __name__ == '__main__':
    main()

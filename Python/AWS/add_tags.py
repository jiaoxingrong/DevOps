#!/bin/env python
#coding: utf-8

import boto3


def ec2_tag(profile, region):
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
                instance_id = instance.instance_id
                for v in  instance.volumes.all():
                    print v.volume_id
                    oVolume = client.Volume(v.volume_id)
                    response = oVolume.create_tags(
                            Tags=[
                                {
                                    'Key': 'Name',
                                    'Value': instance_name
                                },
                                {
                                    'Key': 'Project',
                                    'Value': instance_project
                                }
                            ]
                        )
                    print response

            except Exception,e:
                print Exception, ":", e, instance_name

regions = ['eu-west-1','ap-southeast-1','ap-southeast-2','eu-central-1','ap-northeast-2','ap-northeast-1','us-east-1','sa-east-1','us-west-1','us-west-2']
for region in regions:
    ec2_tag('default', region)

#!/bin/env python
#coding: utf-8
import boto3

def crt_elb(elb_name,instanceIds_list,region):
    session = boto3.session.Session(
        region_name = region
    )
    client = session.client('elb')
    res_crt_elb = client.create_load_balancer(
        LoadBalancerName=elb_name,
        Listeners=[
            {
                'Protocol': 'tcp',
                'LoadBalancerPort': 443,
                'InstanceProtocol': 'tcp',
                'InstancePort': 443,

            },
            {
                'Protocol': 'tcp',
                'LoadBalancerPort': 843,
                'InstanceProtocol': 'tcp',
                'InstancePort': 843,

            },
            {
                'Protocol': 'tcp',
                'LoadBalancerPort': 6001,
                'InstanceProtocol': 'tcp',
                'InstancePort': 6001,

            },
            {
                'Protocol': 'tcp',
                'LoadBalancerPort': 6002,
                'InstanceProtocol': 'tcp',
                'InstancePort': 6002,

            },

        ],
        Subnets=[
                'subnet-3cb75058',
                'subnet-c84854bf',
        ],
        SecurityGroups=[
                'sg-ad3a72c9',
        ],
        Scheme='internet-facing',
        Tags=[
            {
                'Key': 'name',
                'Value': elb_name
            },
        ]
    )
    print res_crt_elb['DNSName']
    res_describe_elb_attr = client.modify_load_balancer_attributes(
        LoadBalancerName = elb_name,
        LoadBalancerAttributes = {

            'CrossZoneLoadBalancing': {
                'Enabled': True
            },

            'ConnectionSettings': {
                'IdleTimeout': 3600
            },
        }
    )
    register_instance_args = []
    for id in instanceIds_list:
        register_instance_args.append({'InstanceId': id})
    res_register_instance = client.register_instances_with_load_balancer(
        LoadBalancerName = elb_name,
        Instances = register_instance_args
    )

def create_route53_record(domain,record,action):
    client = boto3.client('route53')
    response = client.change_resource_record_sets(
        HostedZoneId = "ZBX978R38LFOV",
        ChangeBatch={
            'Comment': domain,
            'Changes': [
                {
                    'Action': action,
                    'ResourceRecordSet': {
                        'Name': domain,
                        'Type': 'CNAME',
                        'ResourceRecords': [
                            {
                                'Value': record,
                            },
                        ],
                        'TTL': 300,
                    }
                },
            ]
        }
    )
    print response

def crt_queue(region,QName):
    session = boto3.session.Session(
        region_name = region
    )
    sqs = session.client('sqs')
    res = sqs.create_queue(
            QueueName=QName,
            Attributes={
                'VisibilityTimeout': '7200',
                'MessageRetentionPeriod': '1209600'
            }
        )
    print res

update_domain = ['naruto-en-cst-svr35.oasgames.com','naruto-en-cst-svr36.oasgames.com','naruto-en-cst-svr37.oasgames.com']

# for domain in update_domain:
create_route53_record(update_domain[0],'elb-naruto-gameserver35-2066929494.ap-southeast-1.elb.amazonaws.com','UPSERT')
create_route53_record(update_domain[1],'elb-naruto-gameserver36-322422656.ap-southeast-1.elb.amazonaws.com','UPSERT')
create_route53_record(update_domain[2],'elb-naruto-gameserver37-1255573817.ap-southeast-1.elb.amazonaws.com','UPSERT')

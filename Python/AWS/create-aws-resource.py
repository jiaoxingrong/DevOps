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
            {
                'Key': 'Project',
                'Value': 'naruto'
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

    res_conf_check =  client.configure_health_check(
        LoadBalancerName=elb_name,
        HealthCheck={
            'Target': 'TCP:36000',
            'Interval': 30,
            'Timeout': 5,
            'UnhealthyThreshold': 2,
            'HealthyThreshold': 10
        }
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
                        'Type': 'A',
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

update_domain = ['a.akar.oasgames.com', 'a.akes.oasgames.com', 'a.akpl.oasgames.com', 'a.aktr.oasgames.com', 'a.botpt.oasgames.com', 'a.caes.oasgames.com', 'a.catr.oasgames.com', 'a.ddtes.oasgames.com', 'a.dhtr.oasgames.com', 'a.eoept.oasgames.com', 'a.gogen.oasgames.com', 'a.goges.oasgames.com', 'a.gogpl.oasgames.com', 'a.gogtr.oasgames.com', 'a.gtest.oasgames.com', 'a.irpt.oasgames.com', 'a.istriketr.oasgames.com', 'a.katr.oasgames.com', 'a.koips4en.oasgames.com', 'a.koips4tw.oasgames.com', 'a.ksde.oasgames.com', 'a.kspt.oasgames.com', 'a.lees.oasgames.com', 'a.lepl.oasgames.com', 'a.lept.oasgames.com', 'a.leru.oasgames.com', 'a.loar.oasgames.com', 'a2.lobr.oasgames.com', 'adm.lobr.oasgames.com', 'a2.lode.oasgames.com', 'a.loel.oasgames.com', 'a2.loes.oasgames.com', 'a.lofr.oasgames.com', 'a.loit.oasgames.com', 'a2.lonl.oasgames.com', 'a2.lopl.oasgames.com', 'a.loru.oasgames.com', 'a2.losv.oasgames.com', 'a2.lotr.oasgames.com', 'a.lyde.oasgames.com', 'a.mwen.oasgames.com', 'a.mwpt.oasgames.com', 'a.mwtr.oasgames.com', 'a.narutode.oasgames.com', 'a.narutoen.oasgames.com', 'a.narutoes.oasgames.com', 'a.narutofr.oasgames.com', 'a.narutopt.oasgames.com', 'adm.odp.oasgames.com', 'a.oktr.oasgames.com', 'a.pwartr.oasgames.com', 'a.sctr.oasgames.com', 'a.slen.oasgames.com', 'a.solen.oasgames.com', 'a.sosde.oasgames.com', 'a.tigerknighten.oasgames.com', 'a.wftr.oasgames.com', 'a.zgtw.oasgames.com']

# crt_elb('elb-naruto-gameserver39',['i-0d673918ec8956181'],'ap-southeast-1')
# crt_elb('elb-naruto-gameserver40',['i-0f16391237b374c18'],'ap-southeast-1')
for domain in update_domain:
    create_route53_record(domain, '34.194.126.123', 'UPSERT')

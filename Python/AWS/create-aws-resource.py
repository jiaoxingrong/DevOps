#!/bin/env python
#coding: utf-8
import boto3

def crt_elb(elb_name,instanceIds_list,region):
    session = boto3.session.Session(
        profile_name='games',
        region_name=region
    )
    client = session.client('elb')

    res_crt_elb = client.create_load_balancer(
        LoadBalancerName=elb_name,
        Listeners=[
         {
                'Protocol': 'tcp',
                'LoadBalancerPort': 10201,
                'InstanceProtocol': 'tcp',
                'InstancePort': 10201,
          },


          {
                'Protocol': 'tcp',
                'LoadBalancerPort': 10202,
                'InstanceProtocol': 'tcp',
                'InstancePort': 10202,
          },


          {
                'Protocol': 'tcp',
                'LoadBalancerPort': 10203,
                'InstanceProtocol': 'tcp',
                'InstancePort': 10203,
          },


          {
                'Protocol': 'tcp',
                'LoadBalancerPort': 10204,
                'InstanceProtocol': 'tcp',
                'InstancePort': 10204,
          },


          {
                'Protocol': 'tcp',
                'LoadBalancerPort': 10205,
                'InstanceProtocol': 'tcp',
                'InstancePort': 10205,
          },


          {
                'Protocol': 'tcp',
                'LoadBalancerPort': 10206,
                'InstanceProtocol': 'tcp',
                'InstancePort': 10206,
          },


          {
                'Protocol': 'tcp',
                'LoadBalancerPort': 10207,
                'InstanceProtocol': 'tcp',
                'InstancePort': 10207,
          },


          {
                'Protocol': 'tcp',
                'LoadBalancerPort': 10208,
                'InstanceProtocol': 'tcp',
                'InstancePort': 10208,
          },


          {
                'Protocol': 'tcp',
                'LoadBalancerPort': 10209,
                'InstanceProtocol': 'tcp',
                'InstancePort': 10209,
          },


          {
                'Protocol': 'tcp',
                'LoadBalancerPort': 10210,
                'InstanceProtocol': 'tcp',
                'InstancePort': 10210,
          },


          {
                'Protocol': 'tcp',
                'LoadBalancerPort': 10211,
                'InstanceProtocol': 'tcp',
                'InstancePort': 10211,
          },


          {
                'Protocol': 'tcp',
                'LoadBalancerPort': 10212,
                'InstanceProtocol': 'tcp',
                'InstancePort': 10212,
          },


          {
                'Protocol': 'tcp',
                'LoadBalancerPort': 10213,
                'InstanceProtocol': 'tcp',
                'InstancePort': 10213,
          },


          {
                'Protocol': 'tcp',
                'LoadBalancerPort': 10214,
                'InstanceProtocol': 'tcp',
                'InstancePort': 10214,
          },


          {
                'Protocol': 'tcp',
                'LoadBalancerPort': 10215,
                'InstanceProtocol': 'tcp',
                'InstancePort': 10215,
          },


          {
                'Protocol': 'tcp',
                'LoadBalancerPort': 10216,
                'InstanceProtocol': 'tcp',
                'InstancePort': 10216,
          },


          {
                'Protocol': 'tcp',
                'LoadBalancerPort': 10217,
                'InstanceProtocol': 'tcp',
                'InstancePort': 10217,
          },


          {
                'Protocol': 'tcp',
                'LoadBalancerPort': 10218,
                'InstanceProtocol': 'tcp',
                'InstancePort': 10218,
          },


          {
                'Protocol': 'tcp',
                'LoadBalancerPort': 10219,
                'InstanceProtocol': 'tcp',
                'InstancePort': 10219,
          },


          {
                'Protocol': 'tcp',
                'LoadBalancerPort': 10220,
                'InstanceProtocol': 'tcp',
                'InstancePort': 10220,
          },


          {
                'Protocol': 'tcp',
                'LoadBalancerPort': 10221,
                'InstanceProtocol': 'tcp',
                'InstancePort': 10221,
          },


          {
                'Protocol': 'tcp',
                'LoadBalancerPort': 10222,
                'InstanceProtocol': 'tcp',
                'InstancePort': 10222,
          },


          {
                'Protocol': 'tcp',
                'LoadBalancerPort': 10223,
                'InstanceProtocol': 'tcp',
                'InstancePort': 10223,
          },


          {
                'Protocol': 'tcp',
                'LoadBalancerPort': 10224,
                'InstanceProtocol': 'tcp',
                'InstancePort': 10224,
          },


          {
                'Protocol': 'tcp',
                'LoadBalancerPort': 10225,
                'InstanceProtocol': 'tcp',
                'InstancePort': 10225,
          },


          {
                'Protocol': 'tcp',
                'LoadBalancerPort': 10226,
                'InstanceProtocol': 'tcp',
                'InstancePort': 10226,
          },


          {
                'Protocol': 'tcp',
                'LoadBalancerPort': 10227,
                'InstanceProtocol': 'tcp',
                'InstancePort': 10227,
          },


          {
                'Protocol': 'tcp',
                'LoadBalancerPort': 10228,
                'InstanceProtocol': 'tcp',
                'InstancePort': 10228,
          },


          {
                'Protocol': 'tcp',
                'LoadBalancerPort': 10229,
                'InstanceProtocol': 'tcp',
                'InstancePort': 10229,
          },


          {
                'Protocol': 'tcp',
                'LoadBalancerPort': 10230,
                'InstanceProtocol': 'tcp',
                'InstancePort': 10230,
          },
        ],
        Subnets=[
                'subnet-a62feefd',
                'subnet-6d731108',
        ],
        SecurityGroups=[
                'sg-be983bc1',
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
            'Target': 'TCP:3389',
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

def crt_queue(profile, region, QName):
    session = boto3.session.Session(
        profile_name=profile,
        region_name=region
    )
    sqs = session.client('sqs')
    res = sqs.create_queue(
            QueueName=QName,
            # Attributes={
            #     'VisibilityTimeout': '7200',
            #     'MessageRetentionPeriod': '1209600'
            # }
        )
    print res

# update_domain = ['br.oasgames.com', 'fr.oasgames.com', 'tw.oasgames.com', 'zh.oasgames.com']

# crt_elb('elb-TigerKnight-bs2',['i-0ef0782dec0b12054'],'us-east-1')

# for domain in update_domain:
    # create_route53_record(domain, '35.160.142.30', 'UPSERT')

queues = ['pay3-sqs-fengxinxiu', 'pay3-sqs-huangkun', 'pay3-sqs-yizhipeng', 'pay3-sqs-renzengpeng']

for queue in queues:
    crt_queue('beijing', 'cn-north-1', queue)
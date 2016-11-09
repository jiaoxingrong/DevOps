#!/bin/env python
#coding: utf-8
import boto3

def crt_elb(elb_name,instanceIds_list):
    client = boto3.client('elb')
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

#elb_args = {'name':'','listeners':{'tcp': [443,843,6001,6002],'ava_zones': ['ap-southeast-1a','ap-southeast-1b'],'subnet_id': ['subnet-3cb75058','subnet-c84854bf']}
# new_elb_dict = {'elb-naruto-gameserver33': ['i-e534c942'], 'elb-naruto-gameserver32': ['i-e434c943'], 'elb-naruto-gameserver31': ['i-e334c944'], 'elb-naruto-gameserver30': ['i-e234c945'], 'elb-naruto-gameserver29': ['i-e134c946'], 'elb-naruto-gameserver28': ['i-e034c947'], 'elb-naruto-gameserver24': ['i-cf34c968'], 'elb-naruto-gameserver23': ['i-ce34c969'], 'elb-naruto-gameserver22': ['i-cd34c96a'], 'elb-naruto-gameserver21': ['i-cc34c96b'], 'elb-naruto-gameserver20': ['i-cb34c96c'], 'elb-naruto-gameserver19': ['i-ca34c96d'], 'elb-naruto-gameserver18': ['i-c934c96e'], 'elb-naruto-gameserver27': ['i-d734c970'], 'elb-naruto-gameserver26': ['i-d634c971'], 'elb-naruto-gameserver25': ['i-d534c972']}
# for elb_name,ins_id in new_elb_dict.items():
    # crt_elb(elb_name,ins_id)
    # print elb_name,ins_id

# new_route53_record = {'naruto-en-cst-svr34.oasgames.com': 'elb-naruto-gameserver34-1012808580.ap-southeast-1.elb.amazonaws.com', 'naruto-en-cst-svr19.oasgames.com': 'elb-naruto-gameserver19-1313480889.ap-southeast-1.elb.amazonaws.com', 'naruto-en-cst-svr31.oasgames.com': 'elb-naruto-gameserver31-2080269691.ap-southeast-1.elb.amazonaws.com', 'naruto-en-cst-svr30.oasgames.com': 'elb-naruto-gameserver30-1306144278.ap-southeast-1.elb.amazonaws.com', 'naruto-en-cst-svr33.oasgames.com': 'elb-naruto-gameserver33-1507905167.ap-southeast-1.elb.amazonaws.com', 'naruto-en-cst-svr32.oasgames.com': 'elb-naruto-gameserver32-433670128.ap-southeast-1.elb.amazonaws.com', 'naruto-en-cst-svr26.oasgames.com': 'elb-naruto-gameserver26-1755228088.ap-southeast-1.elb.amazonaws.com', 'naruto-en-cst-svr27.oasgames.com': 'elb-naruto-gameserver27-1819030021.ap-southeast-1.elb.amazonaws.com', 'naruto-en-cst-svr24.oasgames.com': 'elb-naruto-gameserver24-1164603705.ap-southeast-1.elb.amazonaws.com', 'naruto-en-cst-svr25.oasgames.com': 'elb-naruto-gameserver25-1467582608.ap-southeast-1.elb.amazonaws.com', 'naruto-en-cst-svr22.oasgames.com': 'elb-naruto-gameserver22-1058696511.ap-southeast-1.elb.amazonaws.com', 'naruto-en-cst-svr23.oasgames.com': 'elb-naruto-gameserver23-505838514.ap-southeast-1.elb.amazonaws.com', 'naruto-en-cst-svr20.oasgames.com': 'elb-naruto-gameserver20-1813581714.ap-southeast-1.elb.amazonaws.com', 'naruto-en-cst-svr21.oasgames.com': 'elb-naruto-gameserver21-933245012.ap-southeast-1.elb.amazonaws.com', 'naruto-en-cst-svr29.oasgames.com': 'elb-naruto-gameserver29-846623463.ap-southeast-1.elb.amazonaws.com'}

update_domain = ['akes.oasgames.com', 'goges.oasgames.com', 'loel.oasgames.com']

for domain in update_domain:
    create_route53_record(domain,'d7hmch1g5l42c.cloudfront.net','UPSERT')

# crt_elb(,'i-26584782')

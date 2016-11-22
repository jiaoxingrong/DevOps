#!/bin/env python
#coding: utf-8

import boto3

def ec2_add_tag(region,ins_id,pro):
        session = boto3.session.Session(
            region_name = region
        )
        ec2 = session.client('ec2')

        try:
            response = ec2.create_tags(
                Resources = ins_id,
                Tags=[
                    {
                        'Key': 'Project',
                        'Value': pro
                    },
                ]
            )
            print response

        except:
            pass

def elb_add_tag(region,elb_name,pro):
    session = boto3.session.Session(
        region_name = region
    )
    elb = session.client('elb')

    response = elb.add_tags(
        LoadBalancerNames = [elb_name],
        Tags=[
            {
                'Key': 'Project',
                'Value': pro
            },
        ]
    )
    print response

inss = ['oas-cluster5-6', 'test-ELB', ]
odp = ['ODP-http-ELB','ODP-ELB','elb-oas-odp-tmp','elb-oas-odp3-web']
# pass = []
# for ins in odp:
elb_add_tag('us-east-1','test-ELB','ops-dev')

#!/bin/env python
#coding: utf-8

from datetime import datetime,timedelta
import json
import boto3
from sqlalchemy import create_engine, Table, Column, MetaData, select, INTEGER, VARCHAR, Float, and_

def ec2_price(region):
    engine = create_engine('mysql://root:123456@localhost:3006/aws_price',encoding='utf-8')
    metadata = MetaData()
    ec2_price = Table('ec2',metadata,
        Column('id',INTEGER,primary_key=True),
        Column('service',VARCHAR(50)),
        Column('region',VARCHAR(50)),
        Column('instance_type',VARCHAR(50)),
        Column('platform',VARCHAR(50)),
        Column('price',Float))
    conn = engine.connect()
    session = boto3.session.Session(
        #aws_access_key_id=access_key,
        #aws_secret_access_key=secret_key,
        region_name=region
    )

    end_time = datetime.utcnow()
    start_time = end_time - timedelta(minutes=10)

    client = session.client('ec2')
    res = client.describe_spot_price_history(
            # DryRun = True,
            StartTime = start_time,
            EndTime = end_time,
            ProductDescriptions=[
                'Windows (Amazon VPC)',
                'Linux/UNIX (Amazon VPC)',
            ],
            AvailabilityZone = region + 'a'
        )
    price_data = res.get('SpotPriceHistory')
    for product in price_data:
        instance_type = product.get('InstanceType')
        platform = product.get('ProductDescription')
        price = product.get('SpotPrice')
        i = ec2_price.insert()
        data = dict(service='ec2',region=region,instance_type=instance_type,platform=platform,price=price)
        r = conn.execute(i,**data)

def ec2_priceV2():
    engine = create_engine('mysql://root:123456@localhost:3006/aws_price',encoding='utf-8')
    metadata = MetaData()
    ec2_price = Table('ec2',metadata,
        Column('id',INTEGER,primary_key=True),
        Column('service',VARCHAR(50)),
        Column('region',VARCHAR(50)),
        Column('instance_type',VARCHAR(50)),
        Column('platform',VARCHAR(50)),
        Column('price',Float))
    conn = engine.connect()

    region_contrast = {'US East (N. Virginia)' : 'us-east-1', 'US East (Ohio)' : 'us-east-2', 'US West (N. California)' : 'us-west-1', 'US West (Oregon)' : 'us-west-2', 'EU (Ireland)' : 'eu-west-1', 'EU (Frankfurt)' : 'eu-central-1', 'Asia Pacific (Tokyo)' : 'ap-northeast-1', 'Asia Pacific (Seoul)' : 'ap-northeast-2', 'Asia Pacific (Singapore)' : 'ap-southeast-1', 'Asia Pacific (Sydney)' : 'ap-southeast-2', 'Asia Pacific (Mumbai)' : 'ap-south-1', 'South America (Sao Paulo)' : 'sa-east-1'}

    res = json.loads(file('/Users/Jerome/Downloads/rds_price.json').read())

    for product in res.get('products'):
        if res.get('products').get(product).get('productFamily') == 'Compute Instance':
            product_attr = res.get('products').get(product).get('attributes')
            product_region = region_contrast.get(product_attr.get('location'))
            if not product_region:
                product_region = 'AWS GovCloud (US)'
            instance_type = product_attr.get('instanceType')
            platform = product_attr.get('operatingSystem')
            deploymentOption = product_attr.get('deploymentOption')
            price_attr = res.get('terms').get('OnDemand').get(product)
            for term_info in price_attr:
                if product in term_info:
                    for key in price_attr.get(term_info).get('priceDimensions'):
                        if product in key:
                            price = price_attr.get(term_info).get('priceDimensions').get(key).get('pricePerUnit').get('USD')

    i = ec2_price.insert()
    data = dict(service='ec2',region=region,instance_type=instance_type,platform=platform,price=price)
    r = conn.execute(i,**data)

Regions = ['us-east-1', 'us-east-2', 'us-west-1', 'us-west-2', 'eu-west-1', 'eu-central-1', 'ap-northeast-1', 'ap-northeast-2', 'ap-southeast-1', 'ap-southeast-2', 'ap-south-1', 'sa-east-1']
# map(ec2_price,Regions)

def rds_price():
    engine = create_engine('mysql://root:123456@localhost:3006/aws_price',encoding='utf-8')
    metadata = MetaData()
    rds_price = Table('rds',metadata,
        Column('id',INTEGER,primary_key=True),
        Column('service',VARCHAR(50)),
        Column('region',VARCHAR(50)),
        Column('instance_type',VARCHAR(50)),
        Column('engine',VARCHAR(50)),
        Column('deploymentOption',VARCHAR(50)),
        Column('price',Float))
    conn = engine.connect()

    region_contrast = {'US East (N. Virginia)' : 'us-east-1', 'US East (Ohio)' : 'us-east-2', 'US West (N. California)' : 'us-west-1', 'US West (Oregon)' : 'us-west-2', 'EU (Ireland)' : 'eu-west-1', 'EU (Frankfurt)' : 'eu-central-1', 'Asia Pacific (Tokyo)' : 'ap-northeast-1', 'Asia Pacific (Seoul)' : 'ap-northeast-2', 'Asia Pacific (Singapore)' : 'ap-southeast-1', 'Asia Pacific (Sydney)' : 'ap-southeast-2', 'Asia Pacific (Mumbai)' : 'ap-south-1', 'South America (Sao Paulo)' : 'sa-east-1'}

    res = json.loads(file('/Users/Jerome/Downloads/rds_price.json').read())

    for product in res.get('products'):
        if res.get('products').get(product).get('productFamily') == 'Database Instance':
            product_attr = res.get('products').get(product).get('attributes')
            product_region = region_contrast.get(product_attr.get('location'))
            if not product_region:
                product_region = 'AWS GovCloud (US)'
            instance_type = product_attr.get('instanceType')
            engine = product_attr.get('databaseEngine')
            deploymentOption = product_attr.get('deploymentOption')
            price_attr = res.get('terms').get('OnDemand').get(product)
            for term_info in price_attr:
                if product in term_info:
                    for key in price_attr.get(term_info).get('priceDimensions'):
                        if product in key:
                            price = price_attr.get(term_info).get('priceDimensions').get(key).get('pricePerUnit').get('USD')

            i = rds_price.insert()
            data = dict(service='rds',region=product_region,instance_type=instance_type,engine=engine,deploymentOption=deploymentOption,price=price)
            r = conn.execute(i,**data)

def redshift_price():
    engine = create_engine('mysql://root:123456@localhost:3006/aws_price',encoding='utf-8')
    metadata = MetaData()
    redshift_price = Table('redshift',metadata,
        Column('id',INTEGER,primary_key=True),
        Column('service',VARCHAR(50)),
        Column('region',VARCHAR(50)),
        Column('instance_type',VARCHAR(50)),
        Column('engine',VARCHAR(50)),
        Column('deploymentOption',VARCHAR(50)),
        Column('price',Float))
    conn = engine.connect()

    region_contrast = {'US East (N. Virginia)' : 'us-east-1', 'US East (Ohio)' : 'us-east-2', 'US West (N. California)' : 'us-west-1', 'US West (Oregon)' : 'us-west-2', 'EU (Ireland)' : 'eu-west-1', 'EU (Frankfurt)' : 'eu-central-1', 'Asia Pacific (Tokyo)' : 'ap-northeast-1', 'Asia Pacific (Seoul)' : 'ap-northeast-2', 'Asia Pacific (Singapore)' : 'ap-southeast-1', 'Asia Pacific (Sydney)' : 'ap-southeast-2', 'Asia Pacific (Mumbai)' : 'ap-south-1', 'South America (Sao Paulo)' : 'sa-east-1'}

    res = json.loads(file('/Users/Jerome/Downloads/redshift_price.json').read())

    for product in res.get('products'):
        if res.get('products').get(product).get('productFamily') == 'Compute Instance':
            product_attr = res.get('products').get(product).get('attributes')
            product_region = region_contrast.get(product_attr.get('location'))
            if not product_region:
                product_region = 'AWS GovCloud (US)'
            instance_type = product_attr.get('instanceType')
            price_attr = res.get('terms').get('OnDemand').get(product)
            for term_info in price_attr:
                if product in term_info:
                    for key in price_attr.get(term_info).get('priceDimensions'):
                        if product in key:
                            price = price_attr.get(term_info).get('priceDimensions').get(key).get('pricePerUnit').get('USD')

            i = redshift_price.insert()
            data = dict(service='redshift',region=product_region,instance_type=instance_type,price=price)
            r = conn.execute(i,**data)

def elasticache_price():
    engine = create_engine('mysql://root:123456@localhost:3006/aws_price',encoding='utf-8')
    metadata = MetaData()
    elasticache_price = Table('elasticache',metadata,
        Column('id',INTEGER,primary_key=True),
        Column('service',VARCHAR(50)),
        Column('region',VARCHAR(50)),
        Column('instance_type',VARCHAR(50)),
        Column('price',Float))
    conn = engine.connect()

    region_contrast = {'US East (N. Virginia)' : 'us-east-1', 'US East (Ohio)' : 'us-east-2', 'US West (N. California)' : 'us-west-1', 'US West (Oregon)' : 'us-west-2', 'EU (Ireland)' : 'eu-west-1', 'EU (Frankfurt)' : 'eu-central-1', 'Asia Pacific (Tokyo)' : 'ap-northeast-1', 'Asia Pacific (Seoul)' : 'ap-northeast-2', 'Asia Pacific (Singapore)' : 'ap-southeast-1', 'Asia Pacific (Sydney)' : 'ap-southeast-2', 'Asia Pacific (Mumbai)' : 'ap-south-1', 'South America (Sao Paulo)' : 'sa-east-1'}

    res = json.loads(file('/Users/Jerome/Downloads/elasticache.json').read())

    for product in res.get('products'):
        if res.get('products').get(product).get('productFamily') == 'Cache Instance':
            product_attr = res.get('products').get(product).get('attributes')
            product_region = region_contrast.get(product_attr.get('location'))
            if not product_region:
                product_region = 'AWS GovCloud (US)'
            instance_type = product_attr.get('instanceType')
            price_attr = res.get('terms').get('OnDemand').get(product)
            for term_info in price_attr:
                if product in term_info:
                    for key in price_attr.get(term_info).get('priceDimensions'):
                        if product in key:
                            price = price_attr.get(term_info).get('priceDimensions').get(key).get('pricePerUnit').get('USD')

            i = elasticache_price.insert()
            data = dict(service='elasticache',region=product_region,instance_type=instance_type,price=price)
            r = conn.execute(i,**data)

elasticache_price()

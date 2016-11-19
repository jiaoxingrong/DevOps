#!/bin/env python
#coding: utf-8

import boto3


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

QueueS = ['odp3-db-sync-us-odp-online-activity', 'odp3-db-sync-us-odp-online-article', 'odp3-db-sync-us-odp-online-articles', 'odp3-db-sync-us-odp-online-category', 'odp3-db-sync-us-odp-online-categorys', 'odp3-db-sync-us-odp-online-game-publish-area', 'odp3-db-sync-us-odp-online-games', 'odp3-db-sync-us-odp-online-gift', 'odp3-db-sync-us-odp-online-giftbag', 'odp3-db-sync-us-odp-online-languages', 'odp3-db-sync-us-odp-online-media', 'odp3-db-sync-us-odp-online-nav', 'odp3-db-sync-us-odp-online-notice', 'odp3-db-sync-us-odp-online-quick', 'odp3-db-sync-us-odp-online-regions', 'odp3-db-sync-us-odp-online-rollserver', 'odp3-db-sync-us-odp-online-seo', 'odp3-db-sync-us-odp-online-servermerge', 'odp3-db-sync-us-odp-online-servers', 'odp3-db-sync-us-odp-online-sitemap', 'odp3-db-sync-us-odp-online-special', 'odp3-db-sync-us-odp-online-specialfile', 'odp3-db-sync-us-odp-online-themes', 'odp3-db-sync-us-odp-online-website-templates', 'odp3-db-sync-us-odp-online-whitelist', 'odp3-db-sync-us-odp-online-user-play-log']

# for queue in QueueS:
#     crt_queue('us-east-1',queue)

session = boto3.session.Session(
    # aws_access_key_id="AKIAIAU3JGOCFYFH7O6Q",
    # aws_secret_access_key="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",
    region_name = 'ap-northeast-1'
)
client = session.client('dynamodb')

res = client.query(
        TableName= 'odp-online-game-publish-area',

    )

print res

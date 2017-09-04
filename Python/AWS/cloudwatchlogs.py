#!/bin/env python
import boto3

session = boto3.Session(
        region_name='us-east-1'
    )
cloudwatchlogs = session.client('logs')

def creategroup(logsgroup):
    try:
        response = cloudwatchlogs.create_log_group(
            logGroupName=logsgroup,
            tags={
                'Name': logsgroup
            }
        )
        print response
    except Exception,e:
        print Exception, ":", e, logsgroup

def putmetric(logsgroup, parameter, snsArn):
    filterName = logsgroup + '-' + parameter + '-logs-filter'
    metricName = logsgroup + '-' + parameter + '-logs-metric'
    creatFilter = cloudwatchlogs.put_metric_filter(
        logGroupName=logsgroup,
        filterName=filterName,
        filterPattern=parameter,
        metricTransformations=[
            {
                'metricName': metricName,
                'metricNamespace': 'LogMetrics',
                'metricValue': '1',
            },
        ]
    )

    print creatFilter

    cloudwatch = session.client('cloudwatch')
    creatAlarm = cloudwatch.put_metric_alarm(
        AlarmName='cloudwatch-logs-' + logsgroup + '-app-encounter-error',
        AlarmDescription='cloudwatch-logs-' + logsgroup + '-app-encounter-error',
        ActionsEnabled=True,
        AlarmActions=[
            snsArn,
        ],
        MetricName=metricName,
        Namespace='LogMetrics',
        Statistic='Sum',
        Period=60,
        EvaluationPeriods=1,
        Threshold=1,
        ComparisonOperator='GreaterThanOrEqualToThreshold',
    )

    print creatAlarm

def main():
    # logsgroup = ['oas-pay2-web1-fbpayv2', 'oas-pay2-web1-getPlacedOrder', 'oas-pay2-web1-mob_pay_callback', 'oas-pay2-web1-oaspay', 'oas-pay2-web1-pay_callback', 'oas-pay2-web1-redirect', 'oas-pay2-web2-fbpayv2', 'oas-pay2-web2-getPlacedOrder', 'oas-pay2-web2-mob_pay_callback', 'oas-pay2-web2-oaspay', 'oas-pay2-web2-pay_callback', 'oas-pay2-web2-redirect']
    logsgroup = ['oas-passport-web1-alert', 'oas-passport-web2-alert', 'oas-passport-web3-alert', 'oas-passport-web4-alert']
    arn = 'arn:aws:sns:us-east-1:027999362592:apollo-app-error'
    for group in logsgroup:
        creategroup(group)
        putmetric(group, 'ALERT', arn)


if __name__ == '__main__':
    main()

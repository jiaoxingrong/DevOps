#!/bin/env python
#coding: utf-8

import boto3
import datetime
import time
from flask import Flask,render_template

app = Flask(__name__)
today = time.strftime('%Y-%m-%d',time.localtime(time.time()))

log_file = 'aws-elb-request' + today + '.log'

def get_cloudwatch(elb_list):
    client = boto3.client('cloudwatch')
    end_time = datetime.datetime.utcnow()
    start_time = end_time - datetime.timedelta(minutes=10)
    end_time = end_time.isoformat()
    start_time = start_time.isoformat()

    f = file(log_file,'a')
    for elb in elb_list:
        response = client.get_metric_statistics(
            Namespace='AWS/ELB',
            MetricName='RequestCount',
            Dimensions=[
                {
                    'Name':'LoadBalancerName',
                    'Value':elb
                }
            ],
            StartTime=start_time,
            EndTime=end_time,
            Period=300,
            Statistics=[
                'Sum'
            ]
        )
        write_res = str(response) + '\n'
        f.write(write_res)
        last_data_point = response['Datapoints'][0]['Sum']
        before_data_point = response['Datapoints'][1]['Sum']
        if last_data_point > before_data_point+before_data_point*0.5:
            return 1
        else:
            return 0
    f.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api')
def api():
    return get_cloudwatch(['ODP-ELB'])

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=80,debug=True)

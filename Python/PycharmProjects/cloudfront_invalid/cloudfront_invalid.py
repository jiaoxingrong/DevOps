#!/usr/bin/env python
# coding: utf-8

import time
import boto3
from flask import Flask, render_template, request

app = Flask(__name__)

token_dict = {'wQD5KYc2Qhcz': ['respwtrcdn.oasgames.com'],
              'bYmvFQp2aBxx': ['cdn-dhtr.oasgames.com'],
              'QVfmlOAp83sc': ['dben-cdn.oasgames.com'],
              'UDCyra7aXXq9': ['download-mobile.oasgames.com']}


def invalid_cdn(domain, urls=''):
    try:
        session = boto3.Session(profile_name='yi')
        cloudfront = session.client('cloudfront')
        api_response = cloudfront.list_distributions()
        dist_items = api_response.get('DistributionList').get('Items')
        for item in dist_items:
            cnames = item.get('Aliases').get('Items')
            if cnames and domain in cnames:
                domain_id = item.get('Id')
    except:
        print '获取 Domain_ID 错误！'
        return False
    
    if not domain_id:
        print 'Domain_ID 为空！'
        return False
    
    if not urls:
        invalid_num = 1
        urls = ['/*']
    else:
        invalid_num = len(urls)
    
    try:
        cloudfront.create_invalidation(
            DistributionId=domain_id,
            InvalidationBatch={
                'Paths': {
                    'Quantity': invalid_num,
                    'Items': urls
                },
                'CallerReference': str(time.time())
            }
        )
        
        return True
    except:
        print '建立失效请求失败！'
        return False


@app.route('/')
def cloudfront():
    return render_template('index.html')


@app.route('/api')
def api():
    domain = request.args.get('domain')
    urls = request.args.get('urls')
    if urls == '*':
        urls = '/*'
    urls_list = urls.split('@@@')
    token = request.args.get('token')
    
    if not token_dict.get(token):
        return 'Token不存在'
    
    if not domain in token_dict.get(token):
        return '请检查域名是否正确，或者您没有刷新该域名的权限'
    
    if invalid_cdn(domain, urls_list):
        return '刷新成功，十分钟左右生效'
    else:
        return '刷新失败，请检查域名是否正确'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9527, debug=True)

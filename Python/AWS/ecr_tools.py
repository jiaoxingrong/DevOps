#!/bin/env python
import boto3
import base64
import commands

def docker_login(profile='default', region='ap-northeast-1'):
    session = boto3.Session(
            profile_name = profile,
            region_name = region
        )
    ecr = session.client('ecr')
    res = ecr.get_authorization_token()
    authData = res.get('authorizationData')[0]
    authToken = authData.get('authorizationToken')
    decode_authToken = base64.b64decode(authToken)
    authUsername = decode_authToken.split(':')[0]
    authPasswd = decode_authToken.split(':')[1]
    authEndpoint = authData.get('proxyEndpoint')
    login_command = 'docker login -u %s -p %s -e none %s' % (authUsername, authPasswd, authEndpoint)
    exec_login = commands.getstatusoutput(login_command)
    exec_output = exec_login[1]
    print exec_output

if __name__ == '__main__':
    docker_login()
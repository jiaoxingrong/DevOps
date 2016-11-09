#!/bin/env python
#coding: utf-8

from flask import Flask,request,make_response
import hashlib
import xml.etree.ElementTree as ET
app = Flask(__name__)

def recv_msg(oriData):
    xmldata = ET.fromstring(oriData)
    fromusername = xmldata.find('FromUserName').text
    tousername = xmldata.find('ToUserName').text
    content = xmldata.find('Content').text
    xmldict = {"FromUserName": fromusername,"ToUserName": tousername,"Content": content}
    return xmldict

def submit_msg(content_dict,type='text'):
    toname = content_dict['ToUserName']
    fromname = content_dict['FromeUserName']
    content = content_dict['Content']
    content = "对啊,%s,然后呢" % (content)

    reply = """
    <xml>
        <ToUserName><![CDATA[%s]]></ToUserName>
        <FromUserName><![CDATA[%s]]></FromUserName>
        <CreateTime>%s</CreateTime>
        <MsgType><![CDATA[text]]></MsgType>
        <Content><![CDATA[%s]]></Content>
        <FuncFlag>0</FuncFlag>
    </xml>
    """
    resp_str = reply % (toname, fromname, int(time.time()), content)
    return resp_str

@app.route('/token')
def token():
    app_id = 'wxd394e09bf96e2038'
    app_secret = '380f26afb7c8de70a18a8d2bd8574903'


    return 'Hello World!'

@app.route('/weixin',methods=['GET','POST'])
def weixin():
    token = 'adfegea1345dfaf;.k,'
    query = request.args
    signature = query.get('signature','')
    timestamp = query.get('timestamp','')
    nonce = query.get('nonce','')
    echostr = query.get('echostr','')
    s = [timestamp,nonce,token]
    s.sort()
    s = ''.join(s)
    if (hashlib.sha1(s).hexdigest() == signature):
        response = echostr
    else:
        response = False
        return '认证失败: 不是微信服务器的请求!'
    if request.method == 'GET':
        return response
    else:
        if response:
            oriData = request.data
            submit_msg(recv_msg(oriData))



if __name__ == '__main__':
    app.run(host='127.0.0.1',port=9527,debug=True)
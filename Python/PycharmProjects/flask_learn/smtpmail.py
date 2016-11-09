#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
__title__ = ''
__author__ = 'Jerome'
__mtime__ = '16/3/31'
# code is far away from bugs with the god animal protecting
    I love animals. They taste delicious.
             ┏┓   ┏┓
            ┏┛┻━━━┛┻┓
            ┃    ☃   ┃
            ┃ ┳┛  ┗┳┃
            ┃    ┻  ┃
            ┗━┓   ┏━┛
              ┃   ┗━━━┓
              ┃ 神兽保佑 ┣┓
              ┃ 永无BUG ! ┏┛
              ┗┓┓┏━┳┓┏┛
               ┃┫┫ ┃┫┫
               ┗┻┛ ┗┻┛
"""
import smtplib
import os
from email.mime.text import MIMEText
mailto_list = ['jiaoxingrong@oasgames.com']
mail_host = 'smtp.163.com'
mail_user = os.environ.get('MAIL_USERNAME')
mail_pass = os.environ.get('MAIL_PASSWORD')
mail_postfix= '163.com'

def send_mail(to_list,sub,content):
    me = 'hello' + '<' + mail_user + '@' + mail_postfix +'>'
    msg = MIMEText(content,_subtype='html',_charset='utf-8')

    msg['Subject'] = sub
    msg['From'] = me
    msg['To'] = ";".join(to_list)

    try:
        s = smtplib.SMTP()
        s.connect(mail_host)
        s.login(mail_user,mail_pass)
        s.sendmail(me,to_list,msg.as_string())
        s.close()
        return True
    except Exception,e:
        print str(e)
        return False

if __name__ == '__main__':
    if send_mail(mailto_list,'hello,test','this is my test mail!'):
        print '发送成功'
    else:
        print '发送失败'

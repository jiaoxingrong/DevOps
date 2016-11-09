#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
__title__ = ''
__author__ = 'Jerome'
__mtime__ = '16/3/29'
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

from flask import  Flask
from flask.ext.mail import Mail,Message
from threading import Thread
import os

mail = Mail()
app = Flask(__name__) 

app.config['MAIL_SERVER'] = 'smtp.163.com'
app.config['MAIL_PORT'] = 25
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
q
# mail.init_app(app) 

def send_async_email(app,msg):
    with app.app_context():
        mail.send(msg)

def send_email(to_list,sub,content):
    msg = Message(sub,sender=app.config['MAIL_USERNAME'],
                  recipients=to_list)
    msg.body = contente
    msg.html = '<p>%s</p>' % msg.body
    thr = Thread(target=send_async_email,args=[app,msg])
    thr.start()
    return thr
send_email(['jiaoxingrong@oasgames.com'],'Yeah','This mail from Flasky')
# @app.route('/')
# def index():
#     msg = Message('Yeah',sender=app.config['MAIL_USERNAME'],
#               recipients=['jiaoxingrong@oasgames.com'])
#     msg.body = 'From flasky ttest mail'
#     # msg.html = '<b>HTML</b>body'
#     # send_async_email(app,msg)
#     mail.send(msg)
#     return 'hello'

# if __name__ == '__main__':
#     app.run(debug=True)


#!/usr/bin/python
#encoding:utf8

import smtplib
from email.mime.text import MIMEText
import os
import argparse
import logging
import datetime

mail_host = 'email-smtp.us-east-1.amazonaws.com'
mail_user = 'xxx'
mail_pass = 'xxx'
mail_postfix = 'xxx'
mail_from_user = 'xxx'


def send_mail(mail_to,subject,content):
    me = mail_user+"<"+mail_user+"@"+mail_postfix+">"
    msg = MIMEText(content,'html','utf-8')
    msg['Subject'] = subject
    msg['From'] = mail_from_user
    msg['to'] = mail_to
    global sendstatus
    global senderr

    try:
        smtp = smtplib.SMTP_SSL()
        smtp.connect(mail_host, 465)
        smtp.login(mail_user, mail_pass)
        smtp.sendmail(me, [mail_to],msg.as_string())
        smtp.close()
        print 'send ok'
        sendstatus = True
    except Exception, e:
        senderr=str(e)
        print senderr
        sendstatus = False

def logwrite(sendstatus,mail_to,content):
    logpath='/var/log/zabbix/alert'

    if not sendstatus:
        content = senderr

    if not os.path.isdir(logpath):
        os.makedirs(logpath)

    t=datetime.datetime.now()
    daytime=t.strftime('%Y-%m-%d')
    daylogfile=logpath+'/'+str(daytime)+'.log'
    logging.basicConfig(filename=daylogfile,level=logging.DEBUG)
    os.system('chown zabbix.zabbix {0}'.format(daylogfile))
    logging.info('*'*130)
    logging.debug(str(t)+' mail send to {0},content is :\n {1}'.format(mail_to,content))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Send mail to user for zabbix alerting')
    parser.add_argument('mail_to',action="store", help='The address of the E-mail that send to user ')
    parser.add_argument('subject',action="store", help='The subject of the E-mail')
    parser.add_argument('content',action="store", help='The content of the E-mail')
    args = parser.parse_args()
    mail_to=args.mail_to
    subject=args.subject
    content=args.content

    send_mail(mail_to,subject,content)
    logwrite(sendstatus,mail_to,content)

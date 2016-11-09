#!/bin/env python
#coding: utf-8

import sys
import time
import os

save_ip_file = 'ip_count.py'
if not os.path.isfile(save_ip_file):
    with file('ip_count.py','w') as ip_count_file:
        ip_count_file.write('ip_count={}')
from ip_count import ip_count

today =  time.strftime('%m%d',time.localtime(time.time()))
save_file_atime = time.strftime("%m%d",time.localtime(os.path.getatime(save_ip_file)))
if today != save_file_atime:
    with file('ip_count_' + today + '.log','wa') as hist_file:
        hist_file.write(str(ip_count))
    with file(save_ip_file,'w') as save_file:
        save_file.write('ip_count={}')
    sys.exit(0)

try:
    log_data = file('/Users/Jerome/Documents/access_ngx.log')
except IOError:
    print 'nginx log file not found!'
    sys.exit(1)

for line in log_data:
    access_ip = line.split()[0]
    if ip_count.get(access_ip):
        ip_count[access_ip] += 1
    else:
        ip_count[access_ip] = 1
with file(save_ip_file,'w') as save_count_file:
    save_count_file.write('ip_count='+str(ip_count))
black_ip_list = [ ip for ip,count in ip_count.iteritems() if count>500 ]
black_ngx_conf = ''

for black_ip in black_ip_list:
    black_ngx_conf += '\t\tdeny ' + black_ip + ';\n'

with file('nginx_vhost.conf') as ngx_conf_tpl:
    ngx_conf_text = ngx_conf_tpl.read()
    wrt_conf_text = ngx_conf_text.replace('@@',black_ngx_conf)

with file('write_ngx.conf','w') as wrt_to_file:
    wrt_to_file.write(wrt_conf_text)

a = os.popen('/usr/local/nginx/sbin/nginx -s reload')
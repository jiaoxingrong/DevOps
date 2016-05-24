#!/usr/bin/env python
#coding: utf-8
from zabbix_api_utils import zab
import pdb
import urllib2
import re
import copy
squrl = 'http://sq-iplist.oasgames.com'
unsqurl = 'http://unsq-iplist.oasgames.com'
sq_ip_field = 2
unsq_ip_field = 1

template = 'shenqu_ping_test'
proxy_name = 'p1.zabbix.brotlab.net'
group = 'legend_online'

def GenHosts(hosturl,ip_field):
    try:
        url_response = urllib2.urlopen(hosturl).read().split('\n')
    except urllib2.URLError as e:
        return 'From url get host error : %s' % e
    hosts_item = {}
    already_add_ip = []
    try:
        for line in url_response:
            host_ip = line.split()[ip_field]
            if host_ip not in already_add_ip:
                already_add_ip.append(host_ip)
                host_name = '_'.join(line.split()[:ip_field])
                #将主机名作为key,主机名+ip的元组作为value赋值给字典hosts_item(使用字典和元组为了提高点儿效率)
                hosts_item[host_name] = host_ip
    except:
        pass
    #返回主机项的字典
    return hosts_item

def main():
    #执行Genhosts函数,传入url和ip字段,取出url上的所有主机
    sq_hosts =  GenHosts(squrl,sq_ip_field)
    unsq_hosts = GenHosts(unsqurl,unsq_ip_field)
    on_url_allhost = copy.copy(sq_hosts)
    on_url_allhost.update(unsq_hosts)
    on_zabbix_allhost = zab.get_group_hosts('legend_online')
    # if not on_zabbix_allhost:
    #     return 'get_group_hosts error!'
    need_add_hostnames = set(on_url_allhost.keys()) - set(on_zabbix_allhost)
    need_del_hostnames = set(on_zabbix_allhost) - set(on_url_allhost.keys())
    #匹配美洲地区神曲主机的正则表达式对象,取出所有神曲主机中在欧洲,需要用proxy代理来监控的主机
    # sq_proxy_re = re.compile("^337pt.*|^brazil.*|^broas.*|^naesp.*|^saesp.*")
    # sq_proxy_hostnames = [ sq_host for sq_host in sq_hosts.keys() if sq_proxy_re.findall(sq_host) ]

    #执行添加主机
    for add_host in need_add_hostnames:
        if zab.add_host(add_host,on_url_allhost[add_host],'legend_online','shenqu_ping_test'):
            print('Add host success : %s') % (on_url_allhost[add_host])
        else:
            print('Add host error: %s %s') % (on_url_allhost[add_host])
    #执行删除主机
    for del_host in need_del_hostnames:
        if zab.del_host(del_host):
            print('Del host success : %s') % (del_host)
        else:
            print('Del host error : %s') % (del_host)

    #执行更新代理
    # zab.proxy_update(proxy_name,sq_proxy_hostnames)

main()

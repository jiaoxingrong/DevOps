#!/usr/bin/env python
# coding: utf-8
# author: Liu Yue

import sys
import time
import json
import urllib2
import re

ZABBIX_URL = 'http://s.zabbix.brotlab.net/zabbix/api_jsonrpc.php'
URL_HEADER = {'Content-Type': 'application/json'}
ZABBIX_USER = 'legend'
ZABBIX_PASS = 'p3ftcKcnyB4fhcX'

hosturl = ('http://sq-iplist.oasgames.com/','http://unsq-iplist.oasgames.com/')
hostkey = (2,1)

class Zabbix_Python_API(object):
    def __init__(self):
        self.url = ZABBIX_URL
        self.header = URL_HEADER
        self.auth_id = self.get_auth_id()

    def get_auth_id(self):
        data = json.dumps(
            {
                'jsonrpc': '2.0',
                'method': 'user.login',
                'params': {
                    'user': ZABBIX_USER,
                    'password': ZABBIX_PASS,
                },
                'id': 0,
            }
        )
        request = urllib2.Request(self.url, data, headers=self.header)
        try:
            result = urllib2.urlopen(request)
        except urllib2.URLError as e:
            print e.code
        else:
            response = json.loads(result.read())
            result.close()
            return response['result']

    def get_data(self, data):
        request = urllib2.Request(self.url, data, headers=self.header)
        try:
            result = urllib2.urlopen(request)
        except urllib2.URLError as e:
            if hasattr(e, 'reason'):
                print 'Reason:', e.reason
            elif hasattr(e, 'code'):
                print 'Code:', e.code
        else:
            response = json.loads(result.read())
            result.close()
            return response

    def get_group_exist(self, group_name):
        data = json.dumps(
            {
                'jsonrpc': '2.0',
                'method': 'hostgroup.get',
                'params': {
                    'output': 'extend',
                    'filter': {
                        'name': [
                            group_name
                        ],
                    },
                },
                'auth': self.auth_id,
                'id': 1,
            }
        )
        res = self.get_data(data)
        if res['result']:
            return res['result'][0]['groupid']
        else:
            return self.host_group_create(group_name)

    def host_group_create(self, group_name):
        data = json.dumps(
            {
                'jsonrpc': '2.0',
                'method': 'hostgroup.create',
                'params': {
                    'name': group_name,
                },
                'auth': self.auth_id,
                'id': 1,
            }
        )
        res = self.get_data(data)
        if res['result']:
            return res['result']['groupids'][0]
        else:
            print 'Create Host_Group Error!'
            sys.exit(1)

    def get_template_id(self, temp_name):
        data = json.dumps(
            {
                'jsonrpc': '2.0',
                'method': 'template.get',
                'params': {
                    'output': 'extend',
                    'filter': {
                        'host': [temp_name, ],
                    },
                },
                'auth': self.auth_id,
                'id': 1,
            }
        )
        res = self.get_data(data)
        if res['result']:
            return res['result'][0]['templateid']
        else:
            print 'Get Template Error!'
            sys.exit(1)

    def get_host_list(self, host_ip):
        data = json.dumps(
            {
                'jsonrpc': '2.0',
                'method': 'host.get',
                'params': {
                    'output': ['hostid', 'name', 'status', 'host'],
                    'selectInterface': ['ip'],
                    'filter': {'interface': [host_ip]}
                },
                'auth': self.auth_id,
                'id': 1,
            }
        )
        res = self.get_data(data)
        if res['result']:
            host = res['result'][0]
            return host['hostid']
        else:
            print 'Get Host Error!'

    def get_host_in_group(self, group_name):
        data = json.dumps(
            {
                'jsonrpc': '2.0',
                'method': 'host.get',
                'params': {
                    'output': ['hostid', 'name', 'status', 'host'],
                    'selectGroups': ['groupid', 'name'],
                    'selectInterfaces': ['ip'],
                },
                'auth': self.auth_id,
                'id': 1,
            }
        )
        res = self.get_data(data)
        host_list = []
        if res['result']:
            for host in res['result']:
                if host['groups'][0]['name'] == group_name:
                    host_list.append(host['interfaces'][0]['ip'])
            return host_list
        else:
            print 'Get Host Error!'
            #sys.exit(1)

    def host_create(self, host_name, host_ip, group_id, temp_id):
        g_list = [{'groupid': group} for group in group_id]
        t_list = [{'templateid': temp} for temp in temp_id]
        data = json.dumps(
            {
                'jsonrpc': '2.0',
                'method': 'host.create',
                'params': {
                    'host': host_name,
                    'interfaces': [
                        {
                            'type': 1,
                            'main': 1,
                            'useip': 1,
                            'ip': host_ip,
                            'dns': '',
                            'port': '10050',
                        },
                    ],
                    'groups': g_list,
                    'templates': t_list,
                },
                'auth': self.auth_id,
                'id': 1,
            }
        )
        res = self.get_data(data)
        if 'result' in res.keys():
            if 'hostids' in res['result']:
                return 1
            else:
                return 0
        else:
            print 'Add Host Error', host_ip
            return 0

    def host_del(self, host_ip):
        host_id = self.get_host_list(host_ip)
        print host_id
        data = json.dumps(
            {
                'jsonrpc': '2.0',
                'method': 'host.delete',
                'params': [host_id],
                'auth': self.auth_id,
                'id': 1
            }
        )
        res = self.get_data(data)
        if 'result' in res.keys():
            print 'Delete Hosts Success!'
            return 0

    def proxy_create(self, proxy_name):
        data = json.dumps(
            {
                'jsonrpc': '2.0',
                'method': 'proxy.create',
                'params': {
                    'host': proxy_name,
                    'status': '5',
                    'hosts': [],
                },
                'auth': self.auth_id,
                'id': 1
            }
        )
        res = self.get_data(data)
        if 'result' in res.keys():
            if 'proxyids' in res['result']:
                return res['result']['proxyids']
            else:
                return 0
        else:
            return 0

    def get_proxy_id(self, proxy_name, get_proxy_hostids=False):
        data = json.dumps(
            {
                'jsonrpc': '2.0',
                'method': 'proxy.get',
                'params': {
                    'output': ['host', 'hosts', 'proxyid', 'name'],
                    'selectInterface': 'extend',
                    'selectHosts': ['host', 'hostid', 'name'],
                },
                'auth': self.auth_id,
                'id': 1,
            }
        )
        res = self.get_data(data)
        if 'result' in res.keys():
            if res['result']:
                for proxy in res['result']:
                    if proxy['host'] == proxy_name:
                        if not get_proxy_hostids:
                            return proxy['proxyid']
                        else:
                            return [x['hostid'] for x in proxy['hosts']]
            else:
                return self.proxy_create(proxy_name)
        else:
            return 0

    def proxy_update(self, proxy_name, keep_former_hosts=True):

        proxy_id = self.get_proxy_id(proxy_name)
        proxy_hosts = []

        for us_host in us_hosts:
            proxy_hosts.append(self.get_host_list(us_host))

        if keep_former_hosts:
            host_list.extend(self.get_proxy_id(proxy_name, True))
        data = json.dumps(
            {
                'jsonrpc': '2.0',
                'method': 'proxy.update',
                'params': {
                    'proxyid': proxy_id,
                    'hosts': proxy_hosts,
                },
                'auth': self.auth_id,
                'id': 1,
            }
        )
        res = self.get_data(data)
        if 'result' in res.keys():
            print 'Proxy Update Success.'

hosts = []
us_hosts = []
def genhost(url,key):
    uniqhost1 = {}
    uniqhost2 = {}
    urldata1 = urllib2.urlopen(url[0]).read().split('\n')
    urldata2 = urllib2.urlopen(url[1]).read().split('\n')
    try:
        for item in urldata1:
            uniqhost1.setdefault(str(item.split()[key[0]]),item.split())
        for item in urldata2:
            uniqhost2.setdefault(str(item.split()[key[1]]),item.split())
    except:
        pass
    hosts1 = uniqhost1.values()
    hosts2 = uniqhost2.values()
    us_hosts_re = re.compile('^337pt.*|^brazil.*|^broas.*|^naesp.*|^saesp.*')
    for item in hosts1:
        if us_hosts_re.findall(item[key[0]]):
            us_hosts.append(item[key[0]])
        tmphost1 = ['_'.join(item[:key[0]]),item[key[0]]]
        hosts.append(tmphost1)
    for item in hosts2:
        tmphost2 = ['_'.join(item[:key[1]]),item[key[1]]]
        hosts.append(tmphost2)

def main():
    genhost(hosturl,hostkey)
    zb = Zabbix_Python_API()
    # zabbix group name, 'api_test'
    group_id = [zb.get_group_exist('legend_online')]
    # group proxy name, 'proxy1'
    proxy_name = 'p1.zabbix.brotlab.net'
    temp_id = [
        zb.get_template_id('shenqu_ping_test')
        ]
    host_list = []
    host_in_group = zb.get_host_in_group('legend_online')

    def ExecAdd():
        for host in hosts:
            try:
                host_ip = host[1]
            except:
                pass
            host_name = host[0]
            if host_ip in host_list:
                continue
            host_list.append(host_ip)
            if host_ip in host_in_group:
                continue
            if zb.host_create(host_name,
                              host_ip,
                              group_id,
                              temp_id):
                print 'Add Host Success:', host_ip
        return 'ok'

    if ExecAdd() == 'ok' and host_list:
        for host in host_in_group:
            if host not in host_list:
                zb.host_del(host)
                print 'Del Host:', host
                time.sleep(10)

if __name__ == '__main__':
    main()
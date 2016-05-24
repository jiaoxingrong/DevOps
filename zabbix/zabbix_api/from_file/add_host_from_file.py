#!/usr/bin/env python
# coding: utf-8

import sys
import json
import urllib2
from configparser import ConfigParser

ZABBIX_URL = 'http://s.zabbix.brotlab.net/zabbix/api_jsonrpc.php'
URL_HEADER = {'Content-Type': 'application/json'}
ZABBIX_USER = 'tongyi'
ZABBIX_PASS = 'CZ6Y7yikkD'
HOST_LIST_FILE = 'zbx_new.txt'


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
        except URLError as e:
            print e.code
        else:
            response = json.loads(result.read())
            result.close()
            return response['result']

    def get_data(self, data):
        request = urllib2.Request(self.url, data, headers=self.header)
        try:
            result = urllib2.urlopen(request)
        except URLError as e:
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

    def get_host_list(self, host_ip=[]):
        data = json.dumps(
            {
                'jsonrpc': '2.0',
                'method': 'host.get',
                'params': {
                    'output': ['hostid', 'name', 'status', 'host'],
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
                if host['status'] == '0':
                    if host['interfaces'][0]['ip'] in host_ip:
                        host_list.append(host['hostid'])
            return host_list
        else:
            print 'Get Host Error!'
            sys.exit(1)

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
                            'port': '20050',
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
	    print res
            return 0

    def host_del(self, host_ip):
        host_id_list = self.get_host_list(host_ip)
        data = json.dumps(
            {
                'jsonrpc': '2.0',
                'method': 'host.delete',
                'params': host_id_list,
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

    def proxy_update(self, proxy_name, host_list, keep_former_hosts=True):
        proxy_id = self.get_proxy_id(proxy_name)
        if keep_former_hosts:
            host_list.extend(self.get_proxy_id(proxy_name, True))
        data = json.dumps(
            {
                'jsonrpc': '2.0',
                'method': 'proxy.update',
                'params': {
                    'proxyid': proxy_id,
                    'hosts': host_list,
                },
                'auth': self.auth_id,
                'id': 1,
            }
        )
        res = self.get_data(data)
        if 'result' in res.keys():
            print 'Proxy Update Success.'


def main():
    zb = Zabbix_Python_API()
    # zabbix group name, 'api_test'
    group_id = [zb.get_group_exist('pt_sqyz')]
    # group proxy name, 'proxy1'
    proxy_name = 'p1.zabbix.brotlab.net'
    config = ConfigParser()
    config.read(HOST_LIST_FILE)
    temp_id = [
        # templates name
        zb.get_template_id('Z-Template OS Linux'),
        zb.get_template_id('Z-Template-ICMP and Agent depend proxy1')
        #zb.get_template_id('shenqu_ping_test')
        ]
    host_list = []
    for type in config.sections():
        if type == 'DB':
            temp_id = temp_id + [
                # template_name
                zb.get_template_id('Z-Template MySQL Port'),
            ]
        elif type == 'web':
            temp_id = tem_id + [
                zb.get_template_id('Z-Template App http and php'),
            ]
        elif type == 'web_db':
            temp_id = tem_id + [
                zb.get_template_id('Z-Template App MySQL'),
                zb.get_template_id('Z-Template App http and php'),
            ]
        for host_ip in config.options(type):
            if zb.host_create(config.get(type, host_ip),
                              host_ip,
                              group_id,
                              temp_id):
                print 'Add Host Success:', host_ip
                host_list.append(host_ip)
    host_id_list = zb.get_host_list(host_list)
    #zb.proxy_update(proxy_name, host_id_list)


if __name__ == '__main__':
    main()

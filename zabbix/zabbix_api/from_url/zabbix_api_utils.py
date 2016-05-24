#!/bin/env python
#coding: utf-8
import urllib2
import json

url = 'http://s.zabbix.brotlab.net/zabbix/api_jsonrpc.php'
# url = 'http://10.1.9.151/zabbix/api_jsonrpc.php'
headers = {'Content-Type': 'application/json'}
zabbix_user = 'legend'
zabbix_pass = 'p3ftcKcnyB4fhcX'
# zabbix_user = 'admin'
# zabbix_pass = 'zabbix'
class zabbix_api(object):
    def __init__(self):
        self.auth_id = self.get_auth_id()

    def get_auth_id(self):
        data = json.dumps(
            {
             'jsonrpc': '2.0',
                'method': 'user.login',
                'params': {
                    'user': zabbix_user,
                    'password': zabbix_pass,
                },
                'id': 0,
            }
        )
        api_response = self.get_api_response(data)
        auth_id = api_response.get('result')
        return auth_id

    def get_api_response(self,post_data):
        request = urllib2.Request(url,data=post_data,headers=headers)
        response = urllib2.urlopen(request).read()
        res_data = json.loads(response)
        return res_data

    def get_host_id(self,hostname):
        data = json.dumps(
            {
                "jsonrpc": "2.0",
                "method": "host.get",
                "params": {
                    "output": ['hostid'],
                    "filter": {
                        "host": [
                            hostname
                        ]
                    }
                },
                "auth": self.auth_id,
                "id": 1
            }
        )
        api_response = self.get_api_response(data)
        if api_response.get('result'):
            return api_response.get('result')[0]['hostid']
        else:
            return False

    def get_group_id(self,group):
        data = json.dumps(
                {
                    "jsonrpc": "2.0",
                    "method": "hostgroup.get",
                    "params": {
                        "output": "['groupid']",
                        "filter": {
                            "name": [
                                group
                            ]
                        }
                    },
                    "auth": self.auth_id,
                    "id": 1
                }
        )
        api_response = self.get_api_response(data)
        if api_response.get('result'):
            return api_response.get('result')[0]['groupid']
        else:
            return False

    def get_template_id(self,template):
        data = json.dumps(
            {
                "jsonrpc": "2.0",
                "method": "template.get",
                "params": {
                    "output": "['templateid']",
                    "filter": {
                        "host": [
                            template
                        ]
                    }
                },
                "auth": self.auth_id,
                "id": 1
            }
        )
        api_response = self.get_api_response(data)
        if api_response.get('result'):
            return api_response.get('result')[0]['templateid']
        else:
            return False

    def add_host(self,host_name,host_ip,group,*templates):
        group_id = self.get_group_id(group)
        if not group_id:
            return '%s get group_id error!' % group

        templates_id = []
        for template in templates:
            template_id = self.get_template_id(template)
            if template_id:
                templates_id.append({"templateid":template_id})
            else:
                return '%s get template_id error!' % template
        data = json.dumps(
            {
                "jsonrpc": "2.0",
                "method": "host.create",
                "params": {
                    "host": host_name,
                    "interfaces": [
                        {
                            "type": 1,
                            "main": 1,
                            "useip": 1,
                            "ip": host_ip,
                            "dns": "",
                            "port": "10050"
                        }
                    ],
                    "groups": [
                        {
                            "groupid": group_id
                        }
                    ],
                    "templates": templates_id
                },
                "auth": self.auth_id,
                "id": 1
            }
        )
        api_response = self.get_api_response(data)
        if api_response.get('result'):
            return True

    def del_host(self,host_name):
        host_id = self.get_host_id(host_name)
        if not host_id:
            print '%s get host_id error!' % host_name

        data = json.dumps(
                {
                    "jsonrpc": "2.0",
                    "method": "host.delete",
                    "params": [host_id],
                    "auth": self.auth_id,
                    "id": 1
                }
        )
        api_response = self.get_api_response(data)
        if api_response.get('result'):
            return True

    def get_group_hosts(self,group):
        group_id = self.get_group_id(group)
        if not group_id:
            return '%s get group_id error!' % group
        data = json.dumps(
                {
                    "jsonrpc": "2.0",
                    "method": "host.get",
                    "params": {
                        "output": ['name'],
                        "groupids":group_id
                    },
                    "auth": self.auth_id,
                    "id": 1
                }
        )

        api_response = self.get_api_response(data)
        if api_response.get('result'):
            group_hosts = [ hostitem['name'] for hostitem in api_response.get('result') ]
            return group_hosts
        else:
            return False

    def get_proxy_id(self,proxy_name):
        data = json.dumps(
                {
                    "jsonrpc": "2.0",
                    "method": "proxy.get",
                    "params": {
                        "output": "proxyid",
                        "filter": {
                            'host': proxy_name
                        }
                    },
                    "auth": self.auth_id,
                    "id": 1
                }
        )

        api_response = self.get_api_response(data)
        if api_response.get('result'):
            return api_response.get('result')[0]['proxyid']

    def get_proxy_hosts(self,proxy_name):
        proxy_id = self.get_proxy_id(proxy_name)
        data = json.dumps(
                {
                    "jsonrpc": "2.0",
                    "method": "proxy.get",
                    "params": {
                        "proxyids": proxy_id,
                        "selectHosts": ['hostid']
                    },
                    "auth": self.auth_id,
                    "id": 1
                }
        )

        api_response = self.get_api_response(data)
        if api_response['result']:
            hosts_by_proxy = []
            for api_data in api_response['result'][0]['hosts']:
                hosts_by_proxy.append(api_data['hostid'])
            return hosts_by_proxy
        else:
            print 'Get already monitor by proxy hosts error !'
            print api_response
            return False

    def proxy_update(self,proxy_name,hostname_list):
        proxy_id = self.get_proxy_id(proxy_name)
        if not proxy_id:
            return False

        already_proxy_host = self.get_proxy_hosts(proxy_name)
        if not already_proxy_host:
            return 'Get already_proxy_host error !'

        need_add_hostids = []
        for name in hostname_list:
            host_id = self.get_host_id(name)
            if host_id:
                need_add_hostids.append(host_id)
            else:
                print 'Get host_id error : %s' % (name)

        proxy_add_hosts = already_proxy_host + need_add_hostids
        data = json.dumps(
                {

                    "jsonrpc": "2.0",
                    "method": "proxy.update",
                    "params": {
                        "proxyid": proxy_id,
                        "hosts": proxy_add_hosts
                    },
                    "auth": self.auth_id,
                    "id": 1
                }
        )
        api_response = self.get_api_response(data)
        if api_response.get('result'):
            return True
zab = zabbix_api()

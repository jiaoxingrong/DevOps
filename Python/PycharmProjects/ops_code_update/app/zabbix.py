import urllib
import urllib2
import json

url = 'http://s.zabbix.brotlab.net/zabbix/api_jsonrpc.php'
headers = {'Content-Type': 'application/json'}
zabbix_user = 'legend'
zabbix_pass = 'p3ftcKcnyB4fhcX'

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
        auth_id = api_response['result']
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
        return api_response

zb = zabbix_api()
zb.get_host_id('337pt_0001_DB1Server')
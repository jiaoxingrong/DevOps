#!/usr/bin/env python
import paramiko

hostname = '10.1.9.200'
username = 'root'
passwd = 'xxxxxx'


if __name__ == '__main__':
    paramiko.util.log_to_file('paramiko.log')
    ss = paramiko.SSHClient()
    ss.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ss.connect(hostname=hostname,username=username,password=passwd)
    stdin,stdout,stderr = ss.exec_command('ifconfig;free;df -h')
    print stdout.read()
    ss.close()

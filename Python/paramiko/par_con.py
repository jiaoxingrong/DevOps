#!/usr/bin/env python
#coding:utf-8
import paramiko
import socket,sys,termios,select,tty

def ssh(host,user,password,port=22):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host,username=user,port=port,password=password)
    stdin,stdout,stderr = ssh.exec_command('ls')

    for i in stdout:
        print i.strip('\n')

#ssh('10.1.9.154','root',password='123456')

def sftp(host,user,password,port=22):
    scp = paramiko.Transport((host,port))
    scp.connect(username=user,password=password)
    sftp = paramiko.SFTPClient.from_transport(scp)
    stdout = sftp.listdir('/root')
    for i in stdout:
        print i.strip('\n')
    scp.close()

def posix_shell(chan):
    oldtty = termios.tcgetattr(sys.stdin)
    try:
        tty.setraw(sys.stdin.fileno())
        tty.setcbreak(sys.stdin.fileno())
        chan.settimeout(0.0)
        while True:
            r,w,e = select.select([chan,sys.stdin],[],[])
            if chan in r:
                try:
                    x = chan.recv(1024)
                    if len(x) == 0:
                        print 'rn*** EOFrn',
                        break
                    sys.stdout.write(x)
                    sys.stdout.flush()
                except socket.timeout:
                    pass
            if sys.stdin in r:
                x = sys.stdin.read(1)
                if len(x) == 0:
                    break
                chan.send(x)
    finally:
        termios.tcsetattr(sys.stdin,termios.TCSADRAIN,oldtty)

if __name__ == '__main__':
    paramiko.util.log_to_file('/tmp/par.log')
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.load_system_host_keys()
    ssh.connect('10.1.9.154',username='root',password='123456',compress=True)
    channel=ssh.invoke_shell()
    posix_shell(channel)
    channel.close()
    ssh.close()

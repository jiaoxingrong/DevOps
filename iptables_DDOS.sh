#!/bin/bash
iptables -F
iptables -X
iptables -Z
iptables -F -t nat
iptables -X -t nat
iptables -Z -t nat

#允许SSH进入，要不然等下就连不上去了
iptables -A INPUT -p TCP --dport 22 -j ACCEPT

#设置默认出入站的规则
iptables -P INPUT DROP
iptables -P OUTPUT ACCEPT
iptables -P FORWARD ACCEPT
iptables -A INPUT -i lo -j ACCEPT
iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT

#载入相应的模块
modprobe ip_tables
modprobe iptable_nat
modprobe ip_nat_ftp
modprobe ip_conntrack
modprobe ip_conntrack_ftp

#配置默认的转发规则
iptables -t nat -P PREROUTING ACCEPT
iptables -t nat -P POSTROUTING ACCEPT
iptables -t nat -P OUTPUT ACCEPT

#允许内网连接
#iptables -A INPUT -i 内网网卡名(比如eth1) -j ACCEPT
#iptables -A INPUT -i  -j ACCEPT

#启用转发功能

echo "1" > /proc/sys/net/ipv4/ip_forward

#iptables -t nat -A PREROUTING -p tcp -d 10.1.5.240 -j DNAT --to-destination 10.1.9.187
#iptables -t nat -A POSTROUTING -p tcp -s 10.1.9.187 -j SNAT --to-source 10.1.5.240


pro='tcp'
NAT_Host='195.69.242.179' #本机ip
Dst_Host='195.69.242.134' #远端ip
#iptables -t nat -A PREROUTING -i eth0 -m $pro -p $pro --dport 80:10000 -j DNAT --to-destination $Dst_Host
iptables -t nat -A PREROUTING -m $pro -p $pro --dport 80:10000 -j DNAT --to-destination $Dst_Host
#iptables -t nat -A POSTROUTING -o eth0 -m $pro -p $pro  -d $Dst_Host -j SNAT --to-source $NAT_Host
iptables -t nat -A POSTROUTING -m $pro -p $pro  -d $Dst_Host -j SNAT --to-source $NAT_Host


/sbin/iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT
/sbin/iptables -A OUTPUT -m state --state ESTABLISHED,RELATED -j ACCEPT

iptables -A INPUT -p TCP --dport 22 -j ACCEPT
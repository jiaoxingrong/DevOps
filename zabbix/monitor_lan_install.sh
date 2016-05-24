#!/bin/bash -
read -p '输入要监控的目标IP地址，以空格分开(存在/etc/zabbix/scripts/lan_ip.txt,后期可添加删除): ' input_ip
mkdir -p /etc/zabbix/scripts/
monitor_ip=(${input_ip})

for i in ${monitor_ip[*]};do
    echo $i > /etc/zabbix/scripts/lan_ip.txt
done
yum install fping -y 

cat >/etc/zabbix/scripts/ping_lan.sh<<'EOF'
#!/bin/bash -
res=`fping -r1 -u < /etc/zabbix/scripts/lan_ip.txt |tr '\n' ' '`
if [[ $res != '' ]];then
    echo $res
else
    echo 0
fi
EOF
chmod +x /etc/zabbix/scripts/ping_lan.sh

echo 'UserParameter=php-fpm.num,netstat -anlp | grep php-fpm | grep :9000 |grep ESTAB | wc -l' > /etc/zabbix/zabbix_agentd.d/php-fpm.conf
echo 'UserParameter=ping.lan,/etc/zabbix/scripts/ping_lan.sh' > /etc/zabbix/zabbix_agentd.d/ping_lan.conf

/etc/init.d/zabbix-agent restart
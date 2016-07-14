#!/bin/bash -

cat > /etc/zabbix/scripts/mysql_slave_delay <<EOF
#!/bin/bash -
[ -e /usr/bin/mysql ] && mysql='/usr/bin/mysql' || mysql='/usr/local/mysql/bin/mysql'
var=\$1
MYSQL_USER=\$2
MYSQL_PASSWORD=\$3
MYSQL_Host=\$4
[ "\${MYSQL_USER}" = '' ]  &&  MYSQL_USER=zabbix
[ "\${MYSQL_PASSWORD}" = '' ]  &&  MYSQL_PASSWORD=zabbix
[ "\${MYSQL_Host}" = '' ]  &&  MYSQL_Host=localhost

if [[ \${var} == 'behind' ]]; then
    [ "\${var}" = '' ]  &&  echo "" || \${mysql} -u\${MYSQL_USER} -p\${MYSQL_PASSWORD}  -h\${MYSQL_Host} -e 'show slave status\G' 2>/dev/null|egrep  'Seconds_Behind_Master' |awk '{print \$2}'
fi
EOF

chmod +x /etc/zabbix/scripts/mysql_slave_delay

echo 'UserParameter=mysql.slave.delay,/etc/zabbix/scripts/mysql_slave_delay behind' >> /etc/zabbix/zabbix_agentd.d/mysql_status.conf

/etc/init.d/zabbix-agent restart